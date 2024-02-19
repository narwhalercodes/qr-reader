# ---------------------------------
# ---------Math Related------------
# ---------------------------------

# todo: actually implement data restoration
def ReedSolomon(data, correction):
    return list(data)

# ---------------------------------
# ---------BMP Related-------------
# ---------------------------------

def getPixelsOfBmp(filename):
    pixels = None
    with open(filename, "rb") as f:
        dibheaderfileoffset = 11
        bytes1 = f.read(dibheaderfileoffset + 4)
        signature = bytes1[:2]
        if signature != "BM":
            print "your image is not a bitmap image. wrong signature."
            f.close()
            return None
        pixelarrayfileoffset = sum([ord(bytes1[10-i]) << 8*i for i in range(4)])
        dibheadersize = sum([ord(bytes1[dibheaderfileoffset+3-i]) << 8*i for i in range(4)])
        if dibheadersize < 20:
            print "cannot read dib header. too short to contain requested fields."
            f.close()
            return None
        if dibheadersize + dibheaderfileoffset > pixelarrayfileoffset:
            print "pixel array offset violates common sense. it should come after the dib header ends."
            f.close()
            return None
        bytes1 += f.read(dibheadersize - 4)
        width = sum([ord(bytes1[dibheaderfileoffset+7-i]) << 8*i for i in range(4)])
        height = sum([ord(bytes1[dibheaderfileoffset+11-i]) << 8*i for i in range(4)])
        planes = sum([ord(bytes1[dibheaderfileoffset+13-i]) << 8*i for i in range(2)])
        bitsperpixel = sum([ord(bytes1[dibheaderfileoffset+15-i]) << 8*i for i in range(2)])
        compression = sum([ord(bytes1[dibheaderfileoffset+19-i]) << 8*i for i in range(4)])
        if width*height > 177*177:
            print "image too large. this program uses 8 bytes to represent a single pixel. keep it tiny please. max is 177x177"
            f.close()
            return None
        if bitsperpixel != 1:
            print "your image is not binary. it has more than 1 bit per pixel."
            f.close()
            return None
        if planes != 0:
            print "planes in the image are not supported."
            f.close()
            return None
        if compression != (1 << 16):
            print "compression is not supported."
            f.close()
            return None
        
        # calculates bitsperpixel*width/8 rounded upwards to a multiple of 4.
        bytesperline = (((bitsperpixel * width - 1) >> 5) + 1) << 2
        f.seek(pixelarrayfileoffset)
        
        # for some reason bitmap images uses the bottom left corner as 0,0 while we use the top left corner as 0,0 hence the backwards loop.
        pixels = [None]*height
        y = height - 1
        while y >= 0:
            linebitmap = f.read(bytesperline)
            pixelline = pixels[y] = [None]*width
            x = 0
            bitind = 7
            while x < width:
                pixelline[x] = (ord(linebitmap[x >> 3]) >> bitind) & 1
                if bitind == 0:
                    bitind = 7
                else:
                    bitind -= 1
                x += 1
            y -= 1
        f.close()
    return pixels

def tryGetImageOnce():
    imageLocation = raw_input("enter location of the image: ")
    if imageLocation == "":
        quit()
    try:
        pixels = getPixelsOfBmp(imageLocation)
    except IOError:
        print "some io exception occured, quitting due to no image."
        quit()
    if pixels is not None:
        return pixels
    else:
        print "quitting due to no image."
        quit()

# ---------------------------------
# ---------QR Related--------------
# ---------------------------------

def versionOf(width, height):
    
    # micro qr codes
    if (width, height) == (11, 11): return "M1"
    if (width, height) == (13, 13): return "M2"
    if (width, height) == (15, 15): return "M3"
    if (width, height) == (17, 17): return "M4"
    
    # qr code version 1 to 40 (starting at 21x21 and ending at 177x177).
    if width == height and (width - 17) % 4 == 0 and 21 <= width <= 177:
         return str((width - 17)/4)
    
    return None

def checkMatch(pixels, strPattern, xStart, yStart):
    width = len(pixels[0])
    height = len(pixels)
    patternWidth = len(strPattern[0])
    patternHeight = len(strPattern)
    
    x0 = max(xStart, 0)
    x1 = min(xStart + patternWidth, width)
    y0 = max(yStart, 0)
    y1 = min(yStart + patternHeight, height)
    
    for x in xrange(x0, x1):
        for y in xrange(y0, y1):
            pixel = pixels[y][x]
            expected = strPattern[y - yStart][x - xStart]
            if not (expected == " " or (expected == "1" and pixel == 1) or (expected == "0" and pixel == 0)):
                return False
    
    return True

def positionPatternOf(version):
    return [
        "000000000",
        "011111110",
        "010000010",
        "010111010",
        "010111010",
        "010111010",
        "010000010",
        "011111110",
        "000000000",
    ]

def alignmentPatternOf(version):
    return [
        "11111",
        "10001",
        "10101",
        "10001",
        "11111",
    ]

def alignmentPositionValuesOf(version):
    alignmentPositionValuesTable = [
        [],
        [6,18],
        [6,22],
        [6,26],
        [6,30],
        [6,34],
        [6,22,38],
        [6,24,42],
        [6,26,46],
        [6,28,50],
        [6,30,54],
        [6,32,58],
        [6,34,62],
        [6,26,46,66],
        [6,26,48,70],
        [6,26,50,74],
        [6,30,54,78],
        [6,30,56,82],
        [6,30,58,86],
        [6,34,62,90],
        [6,28,50,72,94],
        [6,26,50,74,98],
        [6,30,54,78,102],
        [6,28,54,80,106],
        [6,32,58,84,110],
        [6,30,58,86,114],
        [6,34,62,90,118],
        [6,26,50,74,98,122],
        [6,30,54,78,102,126],
        [6,26,52,78,104,130],
        [6,30,56,82,108,134],
        [6,34,60,86,112,138],
        [6,30,58,86,114,142],
        [6,34,62,90,118,146],
        [6,30,54,78,102,126,150],
        [6,24,50,76,102,128,154],
        [6,28,54,80,106,132,158],
        [6,32,58,84,110,136,162],
        [6,26,54,82,110,138,166],
        [6,30,58,86,114,142,170],
    ]
    
    return alignmentPositionValuesTable[int(version) - 1]

def validateFixedPatternsMicroQR(version, pixels):
    width = len(pixels[0])
    height = len(pixels)
    
    # timing patterns
    
    timingPatternLength = width - 8
    timingPatternHorizontal = ["10"*(timingPatternLength/2) + "1"]
    timingPatternVertical = [[ch] for ch in list(timingPatternHorizontal[0])]
    
    if not checkMatch(pixels, timingPatternHorizontal, 8, 0):
        return False
    if not checkMatch(pixels, timingPatternVertical, 0, 8):
        return False
    
    # position pattern
    
    positionPattern = positionPatternOf(version)
    
    if not checkMatch(pixels, positionPattern, -1, -1):
        return False
    
    return True

def validateFixedPatterns(version, pixels):
    if version[0] == "M":
        return validateFixedPatternsMicroQR(version, pixels)
    
    width = len(pixels[0])
    height = len(pixels)
    
    # dark module pixel
    
    if pixels[height - 7][8] != 1:
        return False
    
    # timing patterns
    
    timingPatternLength = width - 16
    timingPatternHorizontal = ["10"*(timingPatternLength/2) + "1"]
    timingPatternVertical = [[ch] for ch in list(timingPatternHorizontal[0])]
    
    if not checkMatch(pixels, timingPatternHorizontal, 8, 6):
        return False
    if not checkMatch(pixels, timingPatternVertical, 6, 8):
        return False
    
    # position patterns
    
    positionPattern = positionPatternOf(version)
    
    offsetFromEdge = len(positionPattern) - 1
    
    if not checkMatch(pixels, positionPattern, -1, -1):
        return False
    if not checkMatch(pixels, positionPattern, width - offsetFromEdge, -1):
        return False
    if not checkMatch(pixels, positionPattern, -1, height - offsetFromEdge):
        return False
    
    # alignment patterns
    
    alignmentPattern = alignmentPatternOf(version)
    
    alignmentPositionValues = alignmentPositionValuesOf(version)
    lastInd = len(alignmentPositionValues) - 1
    
    for xi, x in enumerate(alignmentPositionValues):
        for yi, y in enumerate(alignmentPositionValues):
            isTopLeft = xi == 0 and yi == 0
            isTopRight = xi == lastInd and yi == 0
            isBottomLeft = xi == 0 and yi == lastInd
            if not (isTopLeft or isTopRight or isBottomLeft):
                correctedX = x - 2
                correctedY = y - 2
                if not checkMatch(pixels, alignmentPattern, correctedX, correctedY):
                    return False
    
    return True

def errorCorrectionLevelOf(format):
    level = [1, 0, 3, 2][format[0] * 2 + format[1]]
    return "LMQH"[level]

def maskPatternOf(format):
    return format[2] * 4 + format[3] * 2 + format[4]

def formatOfMicroQR(version, pixels):
    
    formatMask = [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0]
    
    result = [None] * 15
    resultPointer = 0
    
    y = 8
    for x in xrange(1, 8 + 1):
        result[resultPointer] = pixels[y][x]
        resultPointer += 1
    
    x = 8
    for y in range(1, 7 + 1)[::-1]:
        result[resultPointer] = pixels[y][x]
        resultPointer += 1
    
    for i in xrange(15):
        result[i] = result[i] ^ formatMask[i]
    
    return result

def formatOf(version, pixels):
    if version[0] == "M":
        return formatOfMicroQR(version, pixels)
    
    formatMask = [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0]
    
    result = [None] * 30
    resultPointer = 0
    
    width = len(pixels[0])
    height = len(pixels)
    
    y = 8
    for x in xrange(0, 5 + 1):
        result[resultPointer] = pixels[y][x]
        resultPointer += 1
    
    result[6] = pixels[8][7]
    result[7] = pixels[8][8]
    result[8] = pixels[7][8]
    resultPointer += 3
    
    x = 8
    for y in range(0, 5 + 1)[::-1]:
        result[resultPointer] = pixels[y][x]
        resultPointer += 1
    
    x = 8
    for y in range(height - 7, height - 1 + 1)[::-1]:
        result[resultPointer] = pixels[y][x]
        resultPointer += 1
    
    y = 8
    for x in xrange(width - 8, width - 1 + 1):
        result[resultPointer] = pixels[y][x]
        resultPointer += 1
    
    for i in xrange(30):
        result[i] = result[i] ^ formatMask[i % 15]
    
    if tuple(result[:15]) != tuple(result[15:]):
        print "format data is not correct for the QR code."
    
    return result[:15]

def noDataPixelsFor(version, width, height):
    noDataPixels = [None] * height
    for y in xrange(height):
        noDataPixels[y] = [False] * width
    
    # excess pixels not used
    
    if version[0] == "M":
        print "excess pixels not implemented for micro qr. (todo)"
        quit()
    else:
        excessPixels = [None,0,7,7,7,7,7,0,0,0,0,0,0,0,3,3,3,3,3,3,3,4,4,4,4,4,4,4,3,3,3,3,3,3,3,0,0,0,0,0,0][int(version)]
    
    for i in xrange(excessPixels):
        x = i % 2
        y = height - 9 - (i / 2) - (3 if int(version) >= 7 else 0)
        noDataPixels[y][x] = True
    
    # pixels reserved in corners (position pattern + format info)
    
    if version[0] == "M":
        for y in xrange(9):
            for x in xrange(9):
                noDataPixels[y][x] = True
    else:
        for corner, cornerWidth, cornerHeight in [("top left", 9, 9), ("top right", 8, 9), ("bottom left", 9, 8)]:
            if corner == "top left":
                x0 = 0
                y0 = 0
            elif corner == "top right":
                x0 = width - cornerWidth
                y0 = 0
            else:
                x0 = 0
                y0 = height - cornerHeight
            
            for y in xrange(y0, y0 + cornerHeight):
                for x in xrange(x0, x0 + cornerWidth):
                    noDataPixels[y][x] = True
    
    # pixels reserved for the timing pattern
    
    if version[0] == "M":
        for v in xrange(width):
            noDataPixels[0][v] = True
            noDataPixels[v][0] = True
    else:
        for v in xrange(width):
            noDataPixels[6][v] = True
            noDataPixels[v][6] = True
    
    # pixels reserved for version information (version 7 qr codes or larger has this).
    
    if version[0] != "M" and int(version) >= 7:
        for y in xrange(height - 8 - 3, height - 8):
            for x in xrange(6):
                noDataPixels[y][x] = True
        for y in xrange(6):
            for x in xrange(width - 8 - 3, width - 8):
                noDataPixels[y][x] = True
    
    # pixels reserved for the alignment patterns
    
    alignmentPositionValues = alignmentPositionValuesOf(version)
    lastInd = len(alignmentPositionValues) - 1
    alignmentWidth = 5
    alignmentHeight = 5
    
    for xi, x in enumerate(alignmentPositionValues):
        for yi, y in enumerate(alignmentPositionValues):
            isTopLeft = xi == 0 and yi == 0
            isTopRight = xi == lastInd and yi == 0
            isBottomLeft = xi == 0 and yi == lastInd
            if not (isTopLeft or isTopRight or isBottomLeft):
                correctedX = x - 2
                correctedY = y - 2
                for yIter in xrange(correctedY, correctedY + alignmentHeight):
                    for xIter in xrange(correctedX, correctedX + alignmentWidth):
                        noDataPixels[yIter][xIter] = True
    
    return noDataPixels

def maskFunction(maskPattern, x, y):
    if maskPattern == 0:
        return (x + y) % 2 == 0
    if maskPattern == 1:
        return y % 2 == 0
    if maskPattern == 2:
        return x % 3 == 0
    if maskPattern == 3:
        return (x + y) % 3 == 0
    if maskPattern == 4:
        return (y / 2 + x / 3) % 2 == 0
    if maskPattern == 5:
        return (x * y) % 2 + (x * y) % 3 == 0
    if maskPattern == 6:
        return ((x * y) % 3 + x * y) % 2 == 0
    if maskPattern == 7:
        return ((x * y) % 3 + x + y) % 2 == 0
    print "unknown mask pattern"
    quit()

def unmaskedPixel(maskPattern, pixels, x, y):
    return pixels[y][x] ^ maskFunction(maskPattern, x, y)

def bitStreamOf(version, maskPattern, noDataPixels, pixels):
    if version[0] == "M":
        data, errorCorrection = bitStreamOfMicroQR(version, maskPattern, noDataPixels, pixels)
        return data, errorCorrection
    
    width = len(pixels[0])
    height = len(pixels)
    
    bitStream = [0] * (width * height)
    i = 0
    
    # The bitstream zig-zags up and down in a 2-pixel wide runway starting in the bottom-right corner.
    # The left side of the runway is traversed directly after the right side of the runway.
    # Any pixels that are reserved by the various patterns (alignment/positioning/timing)
    # or otherwise reserved or unused pixels are skiped (reserved by format or leftover less than 8 bits).
    # Further more, the left side timing pattern shifts the runway to the left one pixel when reached.
    
    direction = "up"
    mainX = width - 1
    while mainX > 0:
        if direction == "up":
            y = height - 1
            yEnd = 0
            yStep = -1
        else:
            y = 0
            yEnd = height - 1
            yStep = 1
        
        while True:
            for x in [mainX, mainX - 1]:
                if not noDataPixels[y][x]:
                    bitStream[i] = unmaskedPixel(maskPattern, pixels, x, y)
                    i += 1
            
            if y == yEnd:
                break
            else:
                y += yStep
        
        if direction == "up":
            direction = "down"
        else:
            direction = "up"
        
        if mainX - 2 == 6:
            mainX = 5
        else:
            mainX = mainX - 2
    
    return bitStream

def totalDataErrorBlockLengthAndBlocksAmountOf(version, errorCorrectionLevel):
    longVersion = version + "-" + errorCorrectionLevel
    
    totalDataErrorBlockLengthAndBlocksAmountTable = {
        "1-L": [19, 7, 1 + 0],
        "1-M": [16, 10, 1 + 0],
        "1-Q": [13, 13, 1 + 0],
        "1-H": [9, 17, 1 + 0],
        "2-L": [34, 10, 1 + 0],
        "2-M": [28, 16, 1 + 0],
        "2-Q": [22, 22, 1 + 0],
        "2-H": [16, 28, 1 + 0],
        "3-L": [55, 15, 1 + 0],
        "3-M": [44, 26, 1 + 0],
        "3-Q": [34, 18, 2 + 0],
        "3-H": [26, 22, 2 + 0],
        "4-L": [80, 20, 1 + 0],
        "4-M": [64, 18, 2 + 0],
        "4-Q": [48, 26, 2 + 0],
        "4-H": [36, 16, 4 + 0],
        "5-L": [108, 26, 1 + 0],
        "5-M": [86, 24, 2 + 0],
        "5-Q": [62, 18, 2 + 2],
        "5-H": [46, 22, 2 + 2],
        "6-L": [136, 18, 2 + 0],
        "6-M": [108, 16, 4 + 0],
        "6-Q": [76, 24, 4 + 0],
        "6-H": [60, 28, 4 + 0],
        "7-L": [156, 20, 2 + 0],
        "7-M": [124, 18, 4 + 0],
        "7-Q": [88, 18, 2 + 4],
        "7-H": [66, 26, 4 + 1],
        "8-L": [194, 24, 2 + 0],
        "8-M": [154, 22, 2 + 2],
        "8-Q": [110, 22, 4 + 2],
        "8-H": [86, 26, 4 + 2],
        "9-L": [232, 30, 2 + 0],
        "9-M": [182, 22, 3 + 2],
        "9-Q": [132, 20, 4 + 4],
        "9-H": [100, 24, 4 + 4],
        "10-L": [274, 18, 2 + 2],
        "10-M": [216, 26, 4 + 1],
        "10-Q": [154, 24, 6 + 2],
        "10-H": [122, 28, 6 + 2],
        "11-L": [324, 20, 4 + 0],
        "11-M": [254, 30, 1 + 4],
        "11-Q": [180, 28, 4 + 4],
        "11-H": [140, 24, 3 + 8],
        "12-L": [370, 24, 2 + 2],
        "12-M": [290, 22, 6 + 2],
        "12-Q": [206, 26, 4 + 6],
        "12-H": [158, 28, 7 + 4],
        "13-L": [428, 26, 4 + 0],
        "13-M": [334, 22, 8 + 1],
        "13-Q": [244, 24, 8 + 4],
        "13-H": [180, 22, 12 + 4],
        "14-L": [461, 30, 3 + 1],
        "14-M": [365, 24, 4 + 5],
        "14-Q": [261, 20, 11 + 5],
        "14-H": [197, 24, 11 + 5],
        "15-L": [523, 22, 5 + 1],
        "15-M": [415, 24, 5 + 5],
        "15-Q": [295, 30, 5 + 7],
        "15-H": [223, 24, 11 + 7],
        "16-L": [589, 24, 5 + 1],
        "16-M": [453, 28, 7 + 3],
        "16-Q": [325, 24, 15 + 2],
        "16-H": [253, 30, 3 + 1],
        "17-L": [647, 28, 1 + 5],
        "17-M": [507, 28, 10 + 1],
        "17-Q": [367, 28, 1 + 1],
        "17-H": [283, 28, 2 + 1],
        "18-L": [721, 30, 5 + 1],
        "18-M": [563, 26, 9 + 4],
        "18-Q": [397, 28, 17 + 1],
        "18-H": [313, 28, 2 + 1],
        "19-L": [795, 28, 3 + 4],
        "19-M": [627, 26, 3 + 1],
        "19-Q": [445, 26, 17 + 4],
        "19-H": [341, 26, 9 + 1],
        "20-L": [861, 28, 3 + 5],
        "20-M": [669, 26, 3 + 1],
        "20-Q": [485, 30, 15 + 5],
        "20-H": [385, 28, 15 + 1],
        "21-L": [932, 28, 4 + 4],
        "21-M": [714, 26, 17 + 0],
        "21-Q": [512, 28, 17 + 6],
        "21-H": [406, 30, 19 + 6],
        "22-L": [1006, 28, 2 + 7],
        "22-M": [782, 28, 17 + 0],
        "22-Q": [568, 30, 7 + 1],
        "22-H": [442, 24, 34 + 0],
        "23-L": [1094, 30, 4 + 5],
        "23-M": [860, 28, 4 + 1],
        "23-Q": [614, 30, 11 + 1],
        "23-H": [464, 30, 16 + 1],
        "24-L": [1174, 30, 6 + 4],
        "24-M": [914, 28, 6 + 1],
        "24-Q": [664, 30, 11 + 1],
        "24-H": [514, 30, 30 + 2],
        "25-L": [1276, 26, 8 + 4],
        "25-M": [1000, 28, 8 + 1],
        "25-Q": [718, 30, 7 + 2],
        "25-H": [538, 30, 22 + 1],
        "26-L": [1370, 28, 10 + 2],
        "26-M": [1062, 28, 19 + 4],
        "26-Q": [754, 28, 28 + 6],
        "26-H": [596, 30, 33 + 4],
        "27-L": [1468, 30, 8 + 4],
        "27-M": [1128, 28, 22 + 3],
        "27-Q": [808, 30, 8 + 2],
        "27-H": [628, 30, 12 + 2],
        "28-L": [1531, 30, 3 + 1],
        "28-M": [1193, 28, 3 + 2],
        "28-Q": [871, 30, 4 + 3],
        "28-H": [661, 30, 11 + 3],
        "29-L": [1631, 30, 7 + 7],
        "29-M": [1267, 28, 21 + 7],
        "29-Q": [911, 30, 1 + 3],
        "29-H": [701, 30, 19 + 2],
        "30-L": [1735, 30, 5 + 1],
        "30-M": [1373, 28, 19 + 1],
        "30-Q": [985, 30, 15 + 2],
        "30-H": [745, 30, 23 + 2],
        "31-L": [1843, 30, 13 + 3],
        "31-M": [1455, 28, 2 + 2],
        "31-Q": [1033, 30, 42 + 1],
        "31-H": [793, 30, 23 + 2],
        "32-L": [1955, 30, 17 + 0],
        "32-M": [1541, 28, 10 + 2],
        "32-Q": [1115, 30, 10 + 3],
        "32-H": [845, 30, 19 + 3],
        "33-L": [2071, 30, 17 + 1],
        "33-M": [1631, 28, 14 + 2],
        "33-Q": [1171, 30, 29 + 1],
        "33-H": [901, 30, 11 + 4],
        "34-L": [2191, 30, 13 + 6],
        "34-M": [1725, 28, 14 + 2],
        "34-Q": [1231, 30, 44 + 7],
        "34-H": [961, 30, 59 + 1],
        "35-L": [2306, 30, 12 + 7],
        "35-M": [1812, 28, 12 + 2],
        "35-Q": [1286, 30, 39 + 1],
        "35-H": [986, 30, 22 + 4],
        "36-L": [2434, 30, 6 + 1],
        "36-M": [1914, 28, 6 + 3],
        "36-Q": [1354, 30, 46 + 1],
        "36-H": [1054, 30, 2 + 6],
        "37-L": [2566, 30, 17 + 4],
        "37-M": [1992, 28, 29 + 1],
        "37-Q": [1426, 30, 49 + 1],
        "37-H": [1096, 30, 24 + 4],
        "38-L": [2702, 30, 4 + 1],
        "38-M": [2102, 28, 13 + 3],
        "38-Q": [1502, 30, 48 + 1],
        "38-H": [1142, 30, 42 + 3],
        "39-L": [2812, 30, 20 + 4],
        "39-M": [2216, 28, 40 + 7],
        "39-Q": [1582, 30, 43 + 2],
        "39-H": [1222, 30, 10 + 6],
        "40-L": [2956, 30, 19 + 6],
        "40-M": [2334, 28, 18 + 3],
        "40-Q": [1666, 30, 34 + 3],
        "40-H": [1276, 30, 20 + 6],
    }
    
    totalData, errorBlockLength, blocksAmount = totalDataErrorBlockLengthAndBlocksAmountTable[longVersion]
    return totalData, errorBlockLength, blocksAmount

def dataFromBitStream(version, errorCorrectionLevel, bitStream):
    if version[0] == "M":
        return dataFromBitStreamMicroQR(version, errorCorrectionLevel, bitStream)
    
    totalData, errorBlockLength, blocksAmount = totalDataErrorBlockLengthAndBlocksAmountOf(version, errorCorrectionLevel)
    totalErrorCorrection = blocksAmount * errorBlockLength
    totalBytes = totalData + totalErrorCorrection
    
    blocks = [None] * blocksAmount
    for i in xrange(blocksAmount):
        dataBlockLength = totalData / blocksAmount
        # would be i < totalData % blocksAmount in case they actually used longer length for the first blocks... sigh...
        if i >= blocksAmount - (totalData % blocksAmount):
            dataBlockLength += 1
        dataBlock = [None] * dataBlockLength
        errorBlock = [None] * errorBlockLength
        blocks[i] = [dataBlock, errorBlock]
    
    v = 0
    blockInd = 0
    byteInd = 0
    typeInd = 0
    
    for i in xrange(totalBytes * 8):
        v = (v << 1) | (bitStream[i] & 1)
        
        if i % 8 == 7:
            if i == totalData * 8 + 7:
                typeInd = 1
                blockInd = 0
                byteInd = 0
            
            blocks[blockInd][typeInd][byteInd] = v
            
            if blockInd < blocksAmount - 1:
                blockInd += 1
            else:
                blockInd = 0
                byteInd += 1
                
                # ugly fix to the last blocks having longer length instead of the first blocks
                if typeInd == 0 and totalData % blocksAmount != 0 and byteInd == totalData / blocksAmount:
                    blockInd = blocksAmount - (totalData % blocksAmount)
            
            v = 0
    
    for block in blocks:
        block[0] = ReedSolomon(block[0], block[1])
    
    data = [None] * totalData
    i = 0
    for block in blocks:
        for byte in block[0]:
            data[i] = byte
            i += 1
    
    return data

def dataOf(version, errorCorrectionLevel, maskPattern, noDataPixels, pixels):
    bitStream = bitStreamOf(version, maskPattern, noDataPixels, pixels)
    data = dataFromBitStream(version, errorCorrectionLevel, bitStream)
    return data

def encodingModeOf(data):
    encoding = data[0] >> 4
    if encoding == 1:
        return "Numeric"
    if encoding == 2:
        return "Alphanumeric"
    if encoding == 4:
        return "Byte"
    if encoding == 8:
        return "Kanji"
    print "unknown encoding mode (%d)" % (encoding)
    quit()

def lengthOf(data, encodingMode, version):
    if version[0] == "M":
        length, lengthSize = lengthOfMicroQR(data, encodingMode, version)
        return length, lengthSize
    
    if 1 <= int(version) <= 9:
        versionGroup = 0
    if 10 <= int(version) <= 26:
        versionGroup = 1
    if 27 <= int(version) <= 40:
        versionGroup = 2
    
    if encodingMode == "Numeric":
        encodingIndex = 0
    if encodingMode == "Alphanumeric":
        encodingIndex = 1
    if encodingMode == "Byte":
        encodingIndex = 2
    if encodingMode == "Kanji":
        encodingIndex = 3
    
    lengthSizeTable = [
        [10, 12, 14],
        [9, 11, 13],
        [8, 16, 16],
        [8, 10, 12],
    ]
    
    lengthSize = lengthSizeTable[encodingIndex][versionGroup]
    
    if lengthSize <= 12:
        length = ((data[0] & 0x0F) << (lengthSize - 4)) | (data[1] >> (12 - lengthSize))
    else:
        length = ((data[0] & 0x0F) << (lengthSize - 4)) | (data[1] << (lengthSize - 12)) | (data[1] >> (20 - lengthSize))
    
    return length, lengthSize

def characterDataOf(data, encodingMode, length, lengthSize):
    if encodingMode != "Byte":
        print "only byte mode supported for now."
        quit()
    bits = 8 * length
    if bits + 4 + lengthSize > 8 * len(data):
        print "length is too long"
        quit()
    
    result = [0] * length
    
    for i in xrange(bits):
        
        d1 = i / 8
        d2 = (i + 4 + lengthSize) / 8
        r1 = i % 8
        r2 = (i + 4 + lengthSize) % 8
        
        result[d1] = result[d1] | (((data[d2] >> (7 - r2)) & 1) << (7 - r1))
    
    return result

def characterDataToTxt(characterData, encodingMode):
    if encodingMode == "Numeric":
        return "".join([str(ch) for ch in characterData])
    if encodingMode == "Alphanumeric":
        return "".join(["0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"[ch] for ch in characterData])
    if encodingMode == "Byte":
        return "".join([chr(ch) for ch in characterData])
    if encodingMode == "Kanji":
        print "how the heck do you do kanji encoding LOL."
        quit()
    print "unknown encoding for data to text call."
    quit()

# ---------------------------------
# --------Debug functions----------
# ---------------------------------

def createExpectedBitStream(s, version, errorCorrectionLevel):
    _, lengthSize = lengthOf([0]*24, "Byte", version)
    totalData, errorBlockLength, blocksAmount = totalDataErrorBlockLengthAndBlocksAmountOf(version, errorCorrectionLevel)
    totalBytes = totalData + errorBlockLength * blocksAmount
    bitStream = [0, 1, 0, 0]
    bitStream.extend([(len(s)>>i)&1 for i in range(lengthSize)][::-1])
    for ch in s:
        v = ord(ch)
        bitStream.extend([(v>>i)&1 for i in range(8)][::-1])
    bitStream.extend([None] * (totalData * 8 - len(bitStream)))
    interleavingsAmount = 1 + totalData / blocksAmount
    numberOfLastInterleavings = totalData % blocksAmount
    interleavings = [None] * interleavingsAmount
    for i in range(interleavingsAmount):
        interleavings[i] = []
    i = 0
    for bitIndex, bit in enumerate(bitStream):
        interleavings[i].append(bit)
        if bitIndex % 8 == 7:
            if bitIndex/8 >= interleavingsAmount * (blocksAmount - numberOfLastInterleavings):
                cycleLength = interleavingsAmount
            else:
                cycleLength = interleavingsAmount - 1
            i += 1
            if i == cycleLength:
                i = 0
    newBitStream = []
    for interleaving in interleavings:
        newBitStream.extend(interleaving)
    return newBitStream

def debugMaskPattern(expectedBitStream, noDataPixels, pixels):
    width = len(pixels[0])
    height = len(pixels)
    isMasked = [[None for x in range(width)] for y in range(height)]
    i = 0
    direction = "up"
    mainX = width - 1
    while mainX > 0:
        if direction == "up":
            y = height - 1
            yEnd = 0
            yStep = -1
        else:
            y = 0
            yEnd = height - 1
            yStep = 1
        
        while True:
            for x in [mainX, mainX - 1]:
                if not noDataPixels[y][x]:
                    if not expectedBitStream[i] is None:
                        isMasked[y][x] = expectedBitStream[i] != pixels[y][x]
                    i += 1
                    if i >= len(expectedBitStream):
                        return isMasked
            
            if y == yEnd:
                break
            else:
                y += yStep
        
        if direction == "up":
            direction = "down"
        else:
            direction = "up"
        
        if mainX - 2 == 6:
            mainX = 5
        else:
            mainX = mainX - 2
    
    return isMasked

# ---------------------------------
# ----------Main logic-------------
# ---------------------------------

pixels = tryGetImageOnce()
pixels = [[1-p for p in row] for row in pixels]

width = len(pixels[0])
height = len(pixels)

version = versionOf(width, height)

if version is None:
    print "unknown version, ", width, "x", height

format = formatOf(version, pixels)
errorCorrectionLevel = errorCorrectionLevelOf(format)
maskPattern = maskPatternOf(format)
noDataPixels = noDataPixelsFor(version, width, height)
data = dataOf(version, errorCorrectionLevel, maskPattern, noDataPixels, pixels)
encodingMode = encodingModeOf(data)
length, lengthSize = lengthOf(data, encodingMode, version)
characterData = characterDataOf(data, encodingMode, length, lengthSize)
print version + "-" + errorCorrectionLevel, "(mask: " + str(maskPattern) + ")", "[" + str(length) + " x " + encodingMode + "]"
text = characterDataToTxt(characterData, encodingMode)
hexText = " ".join(["%02X" % (ch & 0xFF) for ch in characterData])
print "data: \"%s\"" % (text)
print "hex: %s" % (hexText)

# debugging

if 0:
    expect = raw_input("expect=")
    expectedBitStream = createExpectedBitStream(expect, version, errorCorrectionLevel)
    maskPatternBig = debugMaskPattern(expectedBitStream, noDataPixels, pixels)
    #print "\n".join(["".join(["~O "[2 if t is None else (1 if t else 0)] for t in row]) for row in maskPatternBig])
    print "\n".join(["".join(["~O "[2 if t is None else (t ^ maskFunction(maskPattern, x, y))] for x, t in enumerate(row)]) for y, row in enumerate(maskPatternBig)])

# tests

# create test images with wolframalpha "qr code ...", rezise using <body style="margin: 10px; background: #FFF;"><image src="image_big.png" style="image-rendering: pixelated; image-rendering: -moz-crisp-edges; width: 45px; height: 45px;"></image></body>
# then select error correcting level of choice in the dropdown options.

# real world test sample
# ../resources/test_images/test_img_blue_moon.bmp
# https://bit.ly/48bJBi8
# (22 out of 26 bytes used)

# test sample from duckduckgo.com
# ../resources/test_images/test_hello_world_duckduck.bmp
# hello world duckduckgo is cool mate
# (35 out of 44 bytes used)

# test sample from wolframalpha.com
# ../resources/test_images/test_wolframalpha_hello_world.bmp
# hello world
# (11 out of 19 bytes used)

# test sample from wolframalpha.com
# ../resources/test_images/test_wolframalpha_abc.bmp
# abcdefghijklmnopqrstuvwxyzhehehoholololxd0123456789ZYXWVABCDEFGH
# (64 out of 66 bytes used)
