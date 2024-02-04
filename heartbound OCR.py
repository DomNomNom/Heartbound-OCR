import numpy as np
from pathlib import Path

from PIL import Image

language_path = Path("./language_fire")
language_path = Path("./language_purple")

screenshots_path = language_path / 'screenshots'
alphabet_path = language_path / 'alphabet'
alphabet_path.mkdir(exist_ok=True)
debug_path = language_path / 'debug'
debug_path.mkdir(exist_ok=True)
# print([x for x in screenshot_path.iterdir()])
# print(dir())

# load alphabet
alphabet = {}
for filepath in alphabet_path.iterdir():
    image = Image.open(filepath)
    key = filepath.stem
    if key == ".png":
        key = " "
    alphabet[key] = np.asarray(image)

oversized_shape = (64, 64, 3)


textboxes = []

for filepath in screenshots_path.iterdir():
    image = Image.open(filepath)
    pixels = np.asarray(image)

    pixels = pixels[:,:,:3] # ignore alpha

    # if len(pixels.shape) > 2:
    #     pixels = pixels.sum(-1) // 3  # easy greyscale

    # pixels /= pixels.max() # transform into 0..1 instead of 0..255

    # scan from middle bottom to white box
    botmost_black = None
    bottom_white_size = 0
    middle_x = pixels.shape[1] // 2
    # white = (255, 255, 255)
    white_threshold = 250

    for y in reversed(range(pixels.shape[0])):
        # scan until the bottom of the text box
        grey = pixels[y, middle_x].sum() / 3
        if grey < white_threshold and bottom_white_size == 0:
            continue

        # scan until the border finishes
        if grey >= white_threshold:
            bottom_white_size += 1
            continue

        botmost_black = y
        break

    # Scan left until white_threshold
    leftmost_black = middle_x
    for x in reversed(range(middle_x)):
        grey = pixels[botmost_black, x].sum() / 3
        if grey >= white_threshold:
            break
        leftmost_black = x

    # Scan up until white_threshold
    topmost_black = botmost_black
    for y in reversed(range(botmost_black)):
        grey = pixels[y, leftmost_black].sum() / 3
        if grey >= white_threshold:
            break
        topmost_black = y

    ht = botmost_black - topmost_black + 1
    pixels = pixels[topmost_black:botmost_black+1,  leftmost_black:int(ht*6.0), ...]


    x_step = ht *.2465
    x_range = np.arange(ht *.099, pixels.shape[1], x_step)
    y_step = ht * .3
    y_range = np.arange(ht * .06, ht, ht * .3)

    # show captured regions
    # pixels2 = pixels.copy()
    # for x in x_range:
    #     x = int(x)
    #     pixels2[:, x] = (255,0,0)
    # for y in y_range:
    #     y = int(y)
    #     pixels2[y, :] = (200,0,0)
    # image2 = Image.fromarray(pixels2)
    # image2.show()


    # translation = ''
    keys = []

    def high_contrast(arr):
        return 255*np.asarray(arr>=128, dtype=arr.dtype)

    # turn things into tiles
    for text_row, y in enumerate(y_range):
        if y+y_step >= pixels.shape[0]:
            continue
        for text_col, x in enumerate(x_range):
            if x+x_step >= pixels.shape[1]:
                continue

            tile = pixels[
                int(y): int(y+y_step),
                int(x): int(x+x_step)
            ]

            # all black
            if (tile < white_threshold).all():
                continue

            # shrink to avoid borders of all black
            while (tile[0,...] < white_threshold).all():
                tile = tile[1:,...]
            while (tile[-1,...] < white_threshold).all():
                tile = tile[:-1,...]
            while (tile[:,0,...] < white_threshold).all():
                tile = tile[:,1:,...]
            while (tile[:,-1,...] < white_threshold).all():
                tile = tile[:,:-1,...]

            # Make a smaller copy with high contrast and
            tile = high_contrast(tile)

            # remove adjacent duplicate rows
            tile2 = np.zeros(oversized_shape, dtype=tile.dtype)
            out_row = 0
            tile2[out_row, :tile.shape[1]] = tile[0]
            for row in tile:
                # print('aaa', row)
                # print('bb', tile2)
                # if (row == tile2[out_row]).all():
                # print(row.shape, tile2[out_row].shape)
                if (row == tile2[out_row, :len(row)]).all():
                    continue
                out_row += 1
                tile2[out_row, :tile.shape[1]] = row

            # remove adjacent duplicate columns
            out_col = 0
            tile3 = np.zeros(oversized_shape, dtype=tile.dtype)
            tile3[:, out_col] = tile2[:, 0]
            for j in range(tile2.shape[1]):
                if (tile2[:, j] == tile3[:, out_col]).all():
                    continue
                out_col += 1
                # print('write', tile2[:, j].sum())
                tile3[:, out_col] = tile2[:, j]

            # print(tile.shape, tile.dtype, tile2.sum())
            tile = tile3

            # reduce size
            reduced_size = tile[:16, :16]
            assert tile.sum() == reduced_size.sum()
            tile = reduced_size

            # Check if its in the alphabet already
            found_letter = False
            for k, v in alphabet.items():
                # # compute the minimal overlapping shape
                # s = tuple(min(a,b) for a,b in zip(tile.shape, v.shape))
                # diff = abs(tile[:s[0], :s[1]] - v[:s[0], :s[1]]).sum()
                # print(f'{text_row},{text_col}   {k}  {diff}')
                # if diff < 1:
                assert v.shape == tile.shape
                if (v == tile).all():
                    keys.append(k)
                    found_letter = True
                    break
            if found_letter:
                continue


            # add new letter to alphabet'
            letter_name = filepath.name+f'.crop_{text_row}_{text_col}'
            alphabet[letter_name] = tile
            tile_img = Image.fromarray(tile)
            tile_img.save(alphabet_path / f'{letter_name}.png')

        # translation += ' '

    # image2.save(debug_path / (filepath.name + ".crop.align.png"))
    # print(np.array(pixels, dtype=int))
    # image2 = Image.fromarray(np.array((pixels)*20055., dtype='int8'))
    # image2.save(debug_path / (filepath.name + ".png"))
    # with open(debug_path / filepath.name, 'w') as f:
    #     f.write('yay')
    # pixel_size = 3.9 ish

    textboxes.append(keys)


import pickle
with open(language_path / 'keys.pickle', 'wb') as f:
    pickle.dump(textboxes, f)

import substitution_breaker
substitution_breaker.decrypt_language(language_path)
