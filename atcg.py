#!/usr/bin/env python

# Created: June 26, 2018
# Last Modified: June 27, 2018
# Created by collective effors of Alex Chan and Josh Burman
# Contact: wy.alex.chan@gmail.com or
# refer to github - https://github.com/brmnjsh/atcg_script)

# This script is designed to take source fastq files and modify their file name and header lines with
# 6 character unique ATCG combinations, placing the reuslts into new, otherwise duplicate files.
# Both the file name and header lines need to have the same combination
# and the file pair (R1 and R2) need to share this combination
# IMPORTANT - no file pair can share their combination with another file pair

import datetime
import sys
from os import listdir
from os.path import isfile, join

# simple log function to tailor logs for specific output
def log(text = ''):
  if text == '':
    return "============================================================================================="
  else:
    return str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")) + ": " + text

# generates full atcg combos that can fit 6 characters (4096)
# combo_items   - the different characts (A,T,C,G [though it could technically be any strings]),
#                 passed as an array.
# count         - the current recursive depth of a genearated combination
# combo         - the combo string, once an end condition is reached, a combo will be generated
#                 and added to the list of 6 character atcg combos (the global variable - final)
# combo_size    - end condition for the recursion depth
def generate_atcg_combos(combo_items, count = 0, combo = '', combo_size = 6):
  global final
  item = 0

  # continue to recures if the count (corresponds to size of current combo being generated)
  # until it reaches 6, at which point it terminates (appends the completed combo to the list [final])
  if count < combo_size:
    while item < len(combo_items):
      generate_atcg_combos(combo_items, count + 1, combo + combo_items[item], combo_size)
      item += 1
  else:
    final.append(combo)

# core file generation
# takes the source files and places the newly generated files in the result path
# currently it solves the pair issue (files designated by R1 and R2) by getting
# only R1 files. Upon iteration, it will aquire the corresponding R2 file and reference that
# to generate the pair from both sources provided
def process_files():
  files = [f for f in listdir(path + source_path) if isfile(join(path + source_path, f))]
  # gets only the R1 files
  files = [ x for x in files if '_R2_' not in x ]

  # this variable will be incremented to access the next 6 character atcg combination
  # for each new pair that is iterated upon, so as to provide uniqueness for each new pair
  file_atcg_ref = 0
  # the number to get the modulus from to find the header lines
  # IMPORTANT - the header lines must be of equal seperation
  # (ie. 0,4,8,..)
  # it is 0 indexed, even though the line numbers in your text editor may show the first line
  # as 1, don't let this deceive you
  header_line_detector = 4

  for file in files:
    file_new = second_part_sub(file, file_atcg_ref)
    ref_file_r1 = open(path + source_path + '/' + file, 'r')
    new_file_r1 = open(path + result_path + '/' + second_part_sub(file, file_atcg_ref),'w')

    file_r2 = file.replace('_R1_', '_R2_')
    file_r2_new = second_part_sub(file_r2, file_atcg_ref)
    ref_file_r2 = open(path + source_path + '/' + file_r2, 'r')
    new_file_r2 = open(path + result_path + '/' + second_part_sub(file_r2, file_atcg_ref), 'w')

    print log("conversion for source files: " + file + " and " + file_r2)

    # generation of new file from reference R1 file
    for i, line in enumerate(ref_file_r1):
      # every fourth line, including the first
      if i % header_line_detector == 0:
        # replace line is where the header is modified to add
        # the unique 6 character atcg combination
        new_file_r1.write(replace_line(line, file_atcg_ref))
      else:
        new_file_r1.write(line)

    print log("new pair conversion complete for file: " + file + " >> " + file_new)

    # generation of new file from reference R2 file
    for i, line in enumerate(ref_file_r2):
      # every fourth line, including the first
      if i % header_line_detector == 0:
        new_file_r2.write(replace_line(line, file_atcg_ref))
      else:
        new_file_r2.write(line)

    print log("new pair conversion complete for file: " + file_r2 + " >> " + file_r2_new)
    print log()

    # memory ain't cheap...well
    ref_file_r1.close()
    new_file_r1.close()
    ref_file_r2.close()
    new_file_r2.close()
    file_atcg_ref += 1

# adds the unique 6 character atcg combination to the file name as well
def second_part_sub(file, file_atcg_ref):
  file_split = file.split('_')
  file_split[1] = final[file_atcg_ref]
  return '_'.join(file_split)

# so far, we only need to modify the actual ATCG combo at the end of the header item
# this will still allow you to modify the other parts of the header, if need be
# *will leave in commented out sections for later use if required.
def replace_line(line, file_atcg_ref):
  l = line.split(':')

  l[0] = '@MISEQ'
  #l[1] = '239'
  #l[2] = '000000000-AJ592'
  #l[3] = '1'
  #l[4] = '1101'
  # l[5] = '14798'
  # l[6] = line_six_split(l[6])
  # l[7] = 'N'
  # l[8] = '0'
  l[9] = final[file_atcg_ref] + '\n'

  return ':'.join(l)

# legacy, during times of uncertainty
# leaving in because why not and who knows
def line_six_split(line_six):
  temp_split = []

  for r in line_six.split(' '):
    if r == '1' or r == '2':
      temp_split.append(r)
    else:
      temp_split.append('2237')

  return ' '.join(temp_split)

# the items used to seed generation
combo_items = ['A','T','C','G']
final = []
# all paths are conextual to location of python script
# so if atcg.py is in ~/home/projects
# and the source files are in ~/projects/project_1/source
# and you want the result files to be in ~/projects/project_1/result
# path = 'project_1/'
# source_path = 'source'
# result_path = 'result'

if len(sys.argv) > 3:
  path = sys.argv[3]
else:
  path = ''

source_path = sys.argv[1]
result_path = sys.argv[2]

print log("generating unique 6 character atcg combinations...")
print log()

generate_atcg_combos(combo_items)

print log("generation complete")
print log()

print log("beginning conversion...")
print log()

process_files()

print log("all conversions complete!")


