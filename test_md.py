import os
import sys
import random
import re

os.chdir('wiki')
header_regex = re.compile("#*\s*Lore\n", re.IGNORECASE)
args = sys.argv[1:]

def lore(args):
  if len(args) == 0:
    insults = ["you ugly retard", "you dusty bitch", "you doss cunt", "mouth breather", "my friend 😊"]
    print(f"Please provide some search terms or type help, {random.choice(insults)}.")
    return

  md_list = [s for s in next(os.walk('.'))[2] if s.endswith(".md") and not s.startswith("Home")]
  lore_entries = []
  for f in md_list:
    with open(f) as file:
      curr_text = file.read()
    match = header_regex.search(curr_text)  
    if not match:
      continue
    # Title, Content
    lore_entries.append([f.split(".")[0], [s.strip() for s in curr_text[match.span()[1]:].strip().split("#")][0]])

  matches = []
  curr_text = None
  words = []

  for curr_title, curr_text in lore_entries:
    # Count the occurrence of each arg in the title of the current file
    title_matches = len([a for a in args if a.lower() in [s.lower() for s in curr_title.split(" ") if s]])

    # Sanitise body of current file into lowercase list of words
    words = [s.strip().lower() for s in re.sub(r'[^\w\s]|\n', '', curr_text).split(" ") if s]
    print(words)
    # Count the occurrence of each arg in the body of the current file
    body_matches = len([a for a in args if a.lower() in words])
    if title_matches == 0 and body_matches == 0:
      continue
    # Append an array in the form of [title_matches, body_matches, text]
    matches.append([title_matches, body_matches, curr_text])    
    
  if len(matches) == 0:
    return

  # Find match item using max(), in a 2d array max will compare all indexes at 0, then 1 and so on until it finds a single result. 
  # We can utilise this to find the lore item that has the most title and body matches. 
  # The text of this entry is then extracted, split and sanitised into individual entries
  best_text =  [s.strip() for s in f'\n{max(matches)[2]}'.split("\n- ") if s]

  if len(best_text) == 0:
    return
  
  # Determine which of the several entries is the best match based on user args
  final_text = [best_text[0]]

  if len(best_text) > 1:
    entry_matches = []
    for text in best_text:
      words = [s.strip().lower() for s in re.sub(r'[^\w\s]|\n', '', text).split(" ") if s]
      entry_count = len([a for a in args if a.lower() in words])
      if entry_count == 0:
        continue
      entry_matches.append([entry_count, text])
    print(f"{entry_matches}")
    # If there is no clear winner (all entry_count's are the same), only remove entries with 0 matches
    if all(e[0] == entry_matches[0][0] for e in entry_matches):
      final_text = [entry[1] for entry in entry_matches]
    else:
      final_text = [max(entry_matches)[1]]

  print(random.choice(final_text))

if __name__ == "__main__":
  lore(args)