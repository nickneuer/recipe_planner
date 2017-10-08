#!/usr/bin/env python

import itertools
import json
from bin.lib.ingredient_cleaning import apply_pipeline

def overlap_distance(a, b):
    a, b = set(a), set(b)
    if len(a.union(b)) == 0:
        score = 0
    else:
        score = 1.0 * len(a.intersection(b)) / len(a.union(b))
    return score

def make_ngrams(s, n=2):
    s = iter(s)
    ngrams = []
    while True:
        ngram = list(itertools.islice(s, n))
        if not ngram:
            break
        ngrams.append(''.join(ngram))
        #
    return ngrams

def string_bigrams(s):
    ret = []
    for word in s.split(' '):
        grams = make_ngrams(word)
        ret += grams
    return ret

def string_distance(s1, s2):
    return overlap_distance(
        string_bigrams(s1), string_bigrams(s2))

def compare_recipies(recipe1, recipe2):
    distance_tracker = {}
    max_reverse_matches = {}
    for r1 in recipe1:
        for r2 in recipe2:
            distance = string_distance(r1, r2)
            # keep track of used LHS ingredients
            if r1 not in max_reverse_matches:
            	max_reverse_matches[r1] = distance
            else:
            	max_reverse_matches[r1] = max(
            		distance, 
            		max_reverse_matches[r1]
            	)
            # store matched RHS ingredients if the LHS matches agree
            if r2 not in distance_tracker:
                distance_tracker[r2] = (r1, distance)
            else:
                if distance > distance_tracker[r2][1] \
                and distance == max_reverse_matches[r1]:
                    distance_tracker[r2] = (r1, distance)
    return distance_tracker

def score_matches(recipe1, recipe2, sameness_threshold=.2):
    r1_length, r2_length = len(recipe1), len(recipe2)
    matches = compare_recipies(recipe1, recipe2)
    matched = 0
    matched_ingredients = []
    for k in matches:
        if matches[k][1] > sameness_threshold:
            matched += 1
            matched_ingredients.append(
                '{0} -- {1}'.format(k, matches[k][0])
            )
    match_score = float(matched) / (r1_length + r2_length - matched)
    matches['match_score'] = match_score
    matches['matched_ingredients'] = matched_ingredients
    return matches

def get_id(url):
    for uid in url.split('/')[::-1]:
        if uid:
            return uid

def iter_recipes(recipes_file):
    with open(recipes_file) as f:
        for recipe in f:
            r = json.loads(recipe)
            r['ingredients'] = [apply_pipeline(s) for s in r['ingredients']]
            yield r


class RecipeDataset(dict):
    #
    def __init__(self, recipes_file, sameness_threshold=.2):
        dict.__init__(self)
        self.sameness_threshold = sameness_threshold
        for recipe in iter_recipes(recipes_file):
            rid = get_id(recipe['url'])
            recipe['rid'] = rid
            self[rid] = recipe

    def get_related_recipes(self, rid):
        related = []
        start_recipe = self[rid]
        for r in self.values():
            if get_id(r['url']) != rid:
                match = score_matches(
                    start_recipe['ingredients'], 
                    r['ingredients']
                )
                match['url'] = r['url']
                match['title'] = r['title'][0]
                related.append(match)
        return sorted(related, key=lambda m: -m['match_score'])


if __name__ == '__main__':
    rid = 'nectarine-galette'
    recipes_file = 'recipe_scraping/data/smitten_kitchen_ingredients.jl'
    recipes = RecipeDataset(recipes_file)
    # get matches
    for r in recipes.get_related_recipes(rid)[0:10]:
        print(json.dumps(r, indent=4))

