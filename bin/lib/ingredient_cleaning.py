#!/usr/bin/env python

import json
import re
from functools import reduce

def strip_spaces(s):
	return re.sub(r'\([^)]*\)', '', s)

def strip_newline(s):
	return s.replace('\n', '')

def strip_parens(s):
	return re.sub(r'\([^)]*\)', '', s)

def strip_prep_words(s):
	return re.sub(r'(\w*ed\w*)', '', s)

def strip_specific_words(s):
	words = [
	    'cup', 'tablespoon', 'teaspoon',
	    'pound', 'large', 'small', 'beaten',
	    'needed', 'chopped', 'ground', 'stirred',
	    'plus', 'divided'
	]
	for m in words:
		regex = r'(\w*' + re.escape(m) + r'\w*)'
		s = re.sub(regex, '', s)
	return s

def strip_measurements(s):
	return re.sub(r'(\w*[0-9]\w*)', '', s)

def strip_non_alpha(s):
	return re.sub(r'([^a-zA-Z\d\s:])', ' ', s)

def normalize_spaces(s):
	normalized = re.sub(r'([ \t]+)', ' ', s)
	return normalized.lstrip(' ').rstrip(' ')

def compose(f, g):
	return lambda x: f(g(x))

def apply_pipeline(s):
	s = s.lower()
	functions = [
	    strip_spaces, strip_newline,
	    strip_measurements, strip_specific_words,
	    strip_non_alpha, strip_parens
	]
	composed = reduce(compose, functions)
	return normalize_spaces(composed(s))

if __name__ == '__main__':
	
	ingredients_file = "recipe_scraping/data/smitten_kitchen_ingredients.jl"
	with open(ingredients_file) as f:
		for line in f:
			recipe = json.loads(line)
			print(recipe['title'][0])
			indent = ' ' * 4
			for i in recipe['ingredients']:
				#print(indent + '---OG---')
				#print(indent + i.replace('\n', ''))
				#print(indent + '---STRIPPED---')
				print(indent + apply_pipeline(i))
			print()
