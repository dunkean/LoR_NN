from scapy.all import *
sniff(filter="ip", prn=lambda x:x.sprintf("{IP:%IP.src% -> %IP.dst%\n}"))

# items = [1,1,3,4,5]
# knapsack = []
# limit = 7

# def print_solutions(current_item, knapsack, current_sum):
#     #if all items have been processed print the solution and return:
#     if current_item == len(items):
#         print(knapsack)
#         return

#     #don't take the current item and go check others
#     print_solutions(current_item + 1, list(knapsack), current_sum)

#     #take the current item if the value doesn't exceed the limit
#     if (current_sum + items[current_item] <= limit):
#         knapsack.append(items[current_item])
#         current_sum += items[current_item]
#         #current item taken go check others
#         print_solutions(current_item + 1, knapsack, current_sum )

# print_solutions(0,knapsack,0)


# from __future__ import print_function
# from ortools.algorithms import pywrapknapsack_solver


# def main():
#     # Create the solver.
#     solver = pywrapknapsack_solver.KnapsackSolver(
#         pywrapknapsack_solver.KnapsackSolver.
#         KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'KnapsackExample')

#     values = [
#         1,1,1,2,1,2
#     ]
#     weights = [[
#        2,2,2,4,2,4
#     ]]
#     capacities = [6]

#     solver.Init(values, weights, capacities)
#     computed_value = solver.Solve()

#     packed_items = []
#     packed_weights = []
#     total_weight = 0
#     print('Total value =', computed_value)
#     for i in range(len(values)):
#         if solver.BestSolutionContains(i):
#             packed_items.append(i)
#             packed_weights.append(weights[0][i])
#             total_weight += weights[0][i]
#     print('Total weight:', total_weight)
#     print('Packed items:', packed_items)
#     print('Packed_weights:', packed_weights)

#     # solver.


# if __name__ == '__main__':
#     main()

# print(
# d = {}
# d["opp_mana"] = 5
# # d["opp_mana"] = 5
# if "mana" in d:
#     print("arg")
# else:
#     print(d["opp_mana"])

# import itertools
# import numpy as np

# attackers = ["A","B","C","D", "E", "F"]
# blockers = ["a","b","c","d", "e", "f"]

# def generate_blk_permutations(atkrs, board):
#     board.extend(["N" for i in range(len(atkrs)+1)])
#     perm = list(itertools.permutations(board, len(atkrs)))
#     perm = list(dict.fromkeys(perm))
#     return perm

# def generate_atk_permutations(board, blkrs):
#     attackers_configs = []
#     for i in range(len(board) + 1):
#         comb = list(itertools.combinations(board,i))
#         attackers_configs.append(comb)
#         print("--- ATTACKERS COMBINATIONS --- of size >", i, "generated", len(comb))    
    
#     blockers_configs = []
#     blkrs.extend(["N" for i in range(len(board) + 1)])
#     for i in range(len(board) + 1):
#         perm = list(itertools.permutations(blkrs,i))
#         perm = list(dict.fromkeys(perm))
#         blockers_configs.append(perm)
#         print("--- BLOCKERS PERMUTATIONS --- of size >", i, "generated", len(perm))

#     combinations = []
#     for i in range(len(board) + 1):
#         for atkrs in attackers_configs[i]:
#             for blkrs in blockers_configs[i]:
#                 combinations.append((atkrs, blkrs))
    
#     print("Total of possible fights", len(combinations))
#     return combinations

# # perm = generate_blk_permutations(attackers, blockers)
# # print(perm)
# # print(len(perm), "combinations")
# configs = generate_atk_permutations(attackers, blockers)
# print(configs)


# # attackers_configs = []
# # for i in range(len(attackers) + 1):
# #     comb = list(itertools.combinations(attackers,i))
# #     attackers_configs.append(comb)
# #     print("--- ATTACKERS COMBINATIONS --- of size >", i, "generated", len(comb))
# #     # print(comb)

# # for i in range(len(attackers) + 1):
# #     blockers.append("N")
# # blockers_configs = []
# # for i in range(len(attackers) + 1):
# #     perm = list(itertools.permutations(blockers,i))
# #     perm = list(dict.fromkeys(perm))
# #     blockers_configs.append(perm)
# #     print("--- BLOCKERS PERMUTATIONS --- of size >", i, "generated", len(perm))
# #     # print(perm)

# # all_possibilities = 0
# # for i in range(len(attackers) + 1):
# #     total = len(attackers_configs[i]) * len(blockers_configs[i])
# #     all_possibilities += total
# #     print("TOTAL combinations for", i, "attackers:", total)
# # print("maximum number of fights>", all_possibilities)

# # list2 = ["a","b","c","d", ""]
# # all_combinations = []
# # list1_permutations = itertools.permutations(list1, len(list2))

# # for each_permutation in list1_permutations:
# #     zipped = zip(each_permutation, list2)
# #     all_combinations.append(list(zipped))

# # all_combinations = list(itertools.permutations([1, 2, 3]))
# # print(all_combinations)

# # all_combinations = [list(zip(each_permutation, list2)) for each_permutation in itertools.permutations(list1, len(list2))]

# # from PIL import Image, ImageOps


# # # def pixelProcRed(intensity):
# # #     if(intensity > 250):    
# # #         return 255
# # #     return 0

# # # def pixelProcBlue(intensity):
# # #     # if(intensity > 250):
# # #         # return 255
# # #     return 0

# # # def pixelProcGreen(intensity):
# # #     if(intensity > 250):
# # #         return 255
# # #     return 0

# # # count = 0
# # # def test_func(value):
# # #     global count
# # #     if count < 200 :
# # #         print(value)
# # #     count += 1
# # #     return value

# # im     = Image.open("./test.png")
# # dat = im.getdata()
# # f = []
# # for d in dat:
# #     if d[0] == 255 and d[1] == 255 and d[2] == 255: #chp catk
# #         f.append((255,255,255))
# #     elif d[0] <=2 and d[1] == 255 and d[2] <=2: #chp catk boost
# #          f.append((255,255,255))
# #     elif d[0] == 255 and d[1] <=2 and d[2] <=2: #chp catk malus
# #          f.append((255,255,255))
# #     elif d[0] <= 176 and d[0] >= 170 and d[1] <= 225 and d[1] >= 219 and d[2] >= 245: #smana
# #          f.append((255,255,255))
# #     elif d[0] <= 205 and d[0] >= 175 and d[1] <= 220 and d[1] >= 190 and d[2] <= 235 and d[2] >= 215: #mana
# #          f.append((255,255,255))
# #     elif d[0] == 245 and d[1] == 245 and d[2] == 250: #hp
# #         f.append((255,255,255))
# #     elif d[0] == 246 and d[1] == 227 and d[2] == 227: #hp
# #         f.append((255,255,255))
# #     else:
# #         f.append((0,0,0))
# #     # hp(245,245,250) (213,215,220)
# # #chpatk(255,255,255) (1,255,0) (255,0,0)
# # #180 194 218  203 211 234
# #     # print(d)
# # im.putdata(f)
# # im = ImageOps.grayscale(im)
# # im = ImageOps.invert(im)
# # im.show()
# # # threshold = 200  
# # # # im = im.point(lambda p: p > threshold and 255) 
# # # im = im.point(test_func)
# # # im.show() 


# # # multiBands      = im.split()
# # # multiBands[0].save("red.png")
# # # multiBands[1].save("green.png")
# # # multiBands[2].save("blue.png")
# # # redBand      = multiBands[0].point(pixelProcRed)
# # # greenBand    = multiBands[1].point(pixelProcGreen)
# # # blueBand     = multiBands[2].point(pixelProcBlue)
# # # redBand.show()
# # # greenBand.show()
# # # blueBand.show()
# # # newImage = Image.merge("RGB", (redBand, greenBand, blueBand))
# # # newImage.show()

# # import win32gui, win32ui, win32con, win32api
# # from ctypes import windll
# # from PIL import Image, ImageOps, ImageEnhance
# # import cv2
# # import pyautogui
# # import mss
# # import time

# # # import d3dshot
# #     # d.capture()
# #     # im = d.get_latest_frame()
# # # from python_imagesearch.imagesearch import imagesearch, region_grabber

# # def low_level_winshot(rect = None):
# #     hdesktop = win32gui.GetDesktopWindow() 
# #     dl, dt, dr, db = win32gui.GetClientRect(hdesktop)
# #     top = dt
# #     left = dl
# #     width = dr - dl
# #     height = db - dt
# #     srcdc = windll.user32.GetWindowDC(0)
# #     memdc = windll.gdi32.CreateCompatibleDC(srcdc)
# #     bmp = windll.gdi32.CreateCompatibleBitmap(srcdc, width, height)
# #     windll.gdi32.SelectObject(memdc, bmp)
# #     windll.gdi32.BitBlt(memdc, 0, 0, width, height, srcdc, left, top, SRCCOPY)        
# #     bmp_header = pack('LHHHH', calcsize('LHHHH'), width, height, 1, 24)
# #     c_bmp_header = c_buffer(bmp_header) 
# #     c_bits = c_buffer(' ' * (height * ((width * 3 + 3) & -4)))
# #     got_bits = ctypes.windll.gdi32.GetDIBits(memdc, bmp, 0, height,
# #                         c_bits, c_bmp_header, DIB_RGB_COLORS)
# # def win_shot(rect = None):
# #     hdesktop = win32gui.GetDesktopWindow() 
# #     dl, dt, dr, db = win32gui.GetClientRect(hdesktop)
# #     top = dt
# #     left = dl
# #     width = dr - dl
# #     height = db - dt
# #     desktop_dc = win32gui.GetWindowDC(hdesktop)
# #     desktop_img_dc = win32ui.CreateDCFromHandle(desktop_dc)
# #     mem_dc = desktop_img_dc.CreateCompatibleDC() 
# #     screenshot = win32ui.CreateBitmap()
# #     if rect == None:
# #         screenshot.CreateCompatibleBitmap(desktop_img_dc, width, height)
# #         mem_dc.SelectObject(screenshot) 
# #     else:
# #         screenshot.CreateCompatibleBitmap(desktop_img_dc, rect[2] - rect[0], rect[3] - rect[1])
# #         mem_dc.SelectObject(screenshot) 

# #     for i in range (3):
# #         if rect == None:
# #             mem_dc.BitBlt((0, 0), (width, height), desktop_img_dc, (left, top),win32con.SRCCOPY) 
# #         else:
# #             mem_dc.BitBlt((0, 0),  (rect[2] - rect[0], rect[3] - rect[1]), desktop_img_dc, (rect[0],rect[1]), win32con.SRCCOPY) 
    
# #         bmpinfo = screenshot.GetInfo()
# #         bmpstr = screenshot.GetBitmapBits(True)
# #         im = Image.frombuffer(
# #             'RGB',
# #             (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
# #             bmpstr, 'raw', 'BGRX', 0, 1)
# #         im.show()
# #         time.sleep(2)
# #     return im

# # def mss_shot(rect = None):
# #     monitor_number = 1
# #     monitor = sct.monitors[1]
# #     screenshot = None
# #     if rect != None:
# #         monitor = {
# #             "top": rect[1],  # 100px from the top
# #             "left": rect[0],  # 100px from the left
# #             "width": rect[2]-rect[0],
# #             "height": rect[3]-rect[1],
# #             "mon": monitor_number,
# #         }
    
# #     screenshot = sct.grab(monitor)
# #     im = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
# #     return im

# # def pyauto_shot(rect = None):
# #     if rect == None:
# #         return pyautogui.screenshot()
# #     else:
# #         return pyautogui.screenshot(region = rect)


# # # d = d3dshot.create()
# # im = None
# # sct = mss.mss()
# # start = time.time()
# # rect = (2000,100,2500,500)
# # win_shot(rect)

# # # for i in range(100):
# # #     # im = win_shot(rect)
# # #     im = pyauto_shot(rect)
# # #     # im = mss_shot(rect)
# # # end = time.time()
# # # #print(end - start)

# # im.show()

# # ## full desktop
# # # win 4-7 sec ok
# # # pyauto 4-7 sec ok
# # # mss 4-7 sec ok

# # ## full rect
# # # 

# # ## full windows ??