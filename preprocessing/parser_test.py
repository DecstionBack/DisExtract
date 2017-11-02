#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

import numpy as np
import argparse
import io
import nltk
import pickle
import requests
import re

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
from os.path import join as pjoin

import json
from itertools import izip

from copy import deepcopy as cp

np.random.seed(123)

def setup_args():
    parser = argparse.ArgumentParser()
    return parser.parse_args()


def test():
    test_items = [
        {
            "sentence": "After release , it received downloadable content , along with an expanded edition in November of that year .",
            "previous_sentence": "It met with positive sales in Japan , and was praised by both Japanese and western critics .",
            "marker": "after",
            "output": None
        },
        {
            "sentence": "After the game 's completion , additional episodes are unlocked , some of them having a higher difficulty than those found in the rest of the game .",
            "previous_sentence": ".",
            "marker": "after",
            "output": None
        },
        {
            "sentence": "After the release of Valkyria Chronicles II , the staff took a look at both the popular response for the game and what they wanted to do next for the series .",
            "previous_sentence": "NA",
            "marker": "after",
            "output": None
        },
        {
            "sentence": "Kotaku 's Richard Eisenbeis was highly positive about the game , citing is story as a return to form after Valkyria Chronicles II and its gameplay being the best in the series .",
            "previous_sentence": "NA",
            "marker": "after",
            "output": None
        },
        {
            "sentence": "Valkyria of the Battlefield 3 : The Flower of the Nameless Oath ) , illustrated by Naoyuki Fujisawa and eventually released in two volumes after being serialized in Dengeki Maoh between 2011 and 2012 ; and Senjō no Valkyria 3 : <unk> Unmei no <unk> <unk> ( 戦場のヴァルキュリア3 <unk> , lit .",
            "previous_sentence": "They were Senjō no Valkyria 3 : Namo <unk> <unk> no Hana ( 戦場のヴァルキュリア3 <unk> , lit .",
            "marker": "after",
            "output": ('eventually released in two volumes', 'being serialized in Dengeki Maoh between 2011 and 2012')
        },
        {
            "sentence": "After taking up residence , her health began to deteriorate .",
            "previous_sentence": "She restored a maisonette in Storrington , Sussex , England , bequeathed by her friend Edith Major , and named it St. Andrew 's .",
            "marker": "after",
            "output": (', her health began to deteriorate .', 'taking up residence')
        },
        {
            "sentence": "While it retained the standard features of the series , it also underwent multiple adjustments , such as making the game more forgiving for series newcomers .",
            "previous_sentence": "The game began development in 2010 , carrying over a large portion of the work done on Valkyria Chronicles II .",
            "marker": "also",
            "output": ('While it retained the standard features of the series', ', it underwent multiple adjustments , such as making the game more forgiving for series newcomers .')
        },
        {
            "sentence": "It was also adapted into manga and an original video animation series .",
            "previous_sentence": "After release , it received downloadable content , along with an expanded edition in November of that year .",
            "marker": "also",
            "output": ('After release , it received downloadable content , along with an expanded edition in November of that year .', 'It was adapted into manga and an original video animation series .')
        },
        {
            "sentence": "There are also love simulation elements related to the game 's two main heroines , although they take a very minor role .",
            "previous_sentence": "After the game 's completion , additional episodes are unlocked , some of them having a higher difficulty than those found in the rest of the game .",
            "marker": "also",
            "output": ("After the game 's completion , additional episodes are unlocked , some of them having a higher difficulty than those found in the rest of the game .", "There are love simulation elements related to the game 's two main heroines , although they take a very minor role .")
        },
        {
            "sentence": "The music was composed by Hitoshi Sakimoto , who had also worked on the previous Valkyria Chronicles games .",
            "previous_sentence": ".",
            "marker": "also",
            "output": None
        },
        {
            "sentence": "Gallian Army Squad 422 , also known as \" The Nameless \" , are a penal military unit composed of criminals , foreign deserters , and military offenders whose real names are erased from the records and thereon officially referred to by numbers .",
            "previous_sentence": "The game takes place during the Second Europan War .",
            "marker": "also",
            "output": None
        },
        {
            "sentence": "In a preview of the TGS demo , Ryan Geddes of IGN was left excited as to where the game would go after completing the demo , along with enjoying the improved visuals over Valkyria Chronicles II .",
            "previous_sentence": ".",
            "marker": "after",
            "output": ('as to where the game would go', 'completing the demo')
        },
        {
            "sentence": "The units comprising the infantry force of Van Dorn 's Army of the West were the 1st and 2nd Arkansas Mounted Rifles were also armed with M1822 flintlocks from the Little Rock Arsenal .",
            "previous_sentence": "The 9th and 10th Arkansas , four companies of Kelly 's 9th Arkansas Battalion , and the 3rd Arkansas Cavalry Regiment were issued flintlock Hall 's Rifles .",
            "marker": "also",
            "output": None
        },
        {
            "sentence": "The Tower Building of the Little Rock Arsenal , also known as U.S. Arsenal Building , is a building located in MacArthur Park in downtown Little Rock , Arkansas .",
            "previous_sentence": ".",
            "marker": "also",
            "output": None
        },
        {
            "sentence": "It has also been the headquarters of the Little Rock Æsthetic Club since 1894 .",
            "previous_sentence": "It was home to the Arkansas Museum of Natural History and Antiquities from 1942 to 1997 and the MacArthur Museum of Arkansas Military History since 2001 .",
            "marker": "also",
            "output": ('It was home to the Arkansas Museum of Natural History and Antiquities from 1942 to 1997 and the MacArthur Museum of Arkansas Military History since 2001 .', 'It has been the headquarters of the Little Rock \xc3\x86sthetic Club since 1894 .')
        },
        {
            "sentence": "It was also the starting place of the Camden Expedition .",
            "previous_sentence": "Besides being the last remaining structure of the original Little Rock Arsenal and one of the oldest buildings in central Arkansas , it was also the birthplace of General Douglas MacArthur , who became the supreme commander of US forces in the South Pacific during World War II .",
            "marker": "also",
            "output": ('Besides being the last remaining structure of the original Little Rock Arsenal and one of the oldest buildings in central Arkansas , it was also the birthplace of General Douglas MacArthur , who became the supreme commander of US forces in the South Pacific during World War II .', 'It was the starting place of the Camden Expedition .')
        },
        {
            "sentence": "Fey 's projects after 2008 include a voice role in the English @-@ language version of the Japanese animated film Ponyo .",
            "previous_sentence": ".",
            "marker": "after",
            "output": None
        },
        {
            "sentence": "The main cave ( Cave 1 , or the Great Cave ) was a Hindu place of worship until Portuguese rule began in 1534 , after which the caves suffered severe damage .",
            "previous_sentence": ".",
            "marker": "after",
            "output": None
        },
        {
            "sentence": "This movement , although not authorized by me , has assumed such an aspect that it becomes my duty , as the executive of this <unk> , to interpose my official authority to prevent a collision between the people of the State and the Federal troops under your command .",
            "previous_sentence": "This movement is prompted by the feeling that pervades the citizens of this State that in the present emergency the arms and munitions of war in the Arsenal should be under the control of the State authorities , in order to their security .",
            "marker": "although",
            "output": None
        },
        {
            "sentence": "Dunnington was selected to head the ordnance works at Little Rock , and although he continued to draw his pay from the Confederate Navy Department , he was placed in charge of all Confederate ordnance activities ( which included artillery functions ) there with the rank of lieutenant colonel .",
            "previous_sentence": "Ponchartrain , which had been brought to Little Rock in hopes of converting it to an ironclad .",
            "marker": "although",
            "output": (', he was placed in charge of all Confederate ordnance activities ( which included artillery functions ) there with the rank of lieutenant colonel', 'he continued to draw his pay from the Confederate Navy Department')
        },
        {
            "sentence": "The development of a national team faces challenges similar to those across Africa , although the national football association has four staff members focusing on women 's football .",
            "previous_sentence": "The Gambia has two youth teams , an under @-@ 17 side that has competed in FIFA U @-@ 17 Women 's World Cup qualifiers , and an under @-@ 19 side that withdrew from regional qualifiers for an under @-@ 19 World Cup .",
            "marker": "although",
            "output": ('The development of a national team faces challenges similar to those across Africa , .', "the national football association has four staff members focusing on women 's football")
        },
        {
            "sentence": "Although this species is discarded when caught , it is more delicate @-@ bodied than other maskrays and is thus unlikely to survive encounters with trawling gear .",
            "previous_sentence": "In the present day , this is mostly caused by Australia 's Northern Prawn Fishery , which operates throughout its range .",
            "marker": "although",
            "output": (', it is more delicate @ \x01 @ bodied than other maskrays and is thus unlikely to survive encounters with trawling gear .', 'this species is discarded when caught')
        },
        {
            "sentence": "In the nineteenth @-@ century , the mound was higher on the western end of the tomb , although this was removed by excavation to reveal the sarsens beneath during the 1920s .",
            "previous_sentence": "The earthen mound that once covered the tomb is now visible only as an undulation approximately 1 foot , 6 inches in height .",
            "marker": "although",
            "output": ('In the nineteenth @ \x01 @ century , the mound was higher on the western end of the tomb , .', 'this was removed by excavation to reveal the sarsens beneath during the 1920s')
        },
        {
            "sentence": "In 1880 , the archaeologist Flinders Petrie included the existence of the stones at \" <unk> \" in his list of Kentish earthworks ; although noting that a previous commentator had described the stones as being in the shape of an oval , he instead described them as forming \" a rectilinear enclosure \" around the chamber .",
            "previous_sentence": "He believed that the monument consisted of both a \" chamber \" and an \" oval \" of stones , suggesting that they were \" two distinct erections \" .",
            "marker": "although",
            "output": (', he instead described them as forming " a rectilinear enclosure " around the chamber', 'noting that a previous commentator had described the stones as being in the shape of an oval')
        },
        {
            "sentence": "She was not damaged although it took over a day to pull her free .",
            "previous_sentence": "Webb demonstrated his aggressiveness when he attempted to sortie on the first spring tide ( 30 May ) after taking command , but Atlanta 's forward engine broke down after he had passed the obstructions , and the ship ran aground .",
            "marker": "although",
            "output": ('She was not damaged .', 'it took over a day to pull her free')
        },
        {
            "sentence": "Valkyria of the Battlefield 3 ) , commonly referred to as Valkyria Chronicles III outside Japan , is a tactical role @-@ playing video game developed by Sega and Media.Vision for the PlayStation Portable .",
            "previous_sentence": "Senjō no Valkyria 3 : <unk> Chronicles ( Japanese : 戦場のヴァルキュリア3 , lit .",
            "marker": "and",
            "output": None
        },
        {
            "sentence": "Employing the same fusion of tactical and real @-@ time gameplay as its predecessors , the story runs parallel to the first game and follows the \" Nameless \" , a penal military unit serving the nation of Gallia during the Second Europan War who perform secret black operations and are pitted against the Imperial unit \" <unk> Raven \" .",
            "previous_sentence": "Released in January 2011 in Japan , it is the third game in the Valkyria series .",
            "marker": "and",
            ## the "who" here is not quite right, but I don't know how to resolve that the way the dependency parse works...
            "output": ('are pitted against the Imperial unit " <unk> Raven', 'who perform secret black operations')
        },
        {
            "sentence": "Character designer <unk> Honjou and composer Hitoshi Sakimoto both returned from previous entries , along with Valkyria Chronicles II director Takeshi Ozawa .",
            "previous_sentence": "While it retained the standard features of the series , it also underwent multiple adjustments , such as making the game more forgiving for series newcomers .",
            "marker": "and",
            "output": None
        },
        {
            "sentence": "It met with positive sales in Japan , and was praised by both Japanese and western critics .",
            "previous_sentence": ".",
            "marker": "and",
            "output": ('was praised by both Japanese and western critics', 'It met with positive sales in Japan , .')
        },
        {
            "sentence": "It was also adapted into manga and an original video animation series .",
            "previous_sentence": "After release , it received downloadable content , along with an expanded edition in November of that year .",
            "marker": "and",
            "output": None
        },
        {
            "sentence": "As with previous <unk> Chronicles games , Valkyria Chronicles III is a tactical role @-@ playing game where players take control of a military unit and take part in missions against enemy forces .",
            "previous_sentence": ".",
            "marker": "and",
            ## the "where" here is not quite right, but I don't know how to resolve that the way the dependency parse works...
            "output": ('take part in missions against enemy forces', 'where players take control of a military unit')
        },
        {
            "sentence": "Stories are told through comic book @-@ like panels with animated character portraits , with characters speaking partially through voiced speech bubbles and partially through unvoiced text .",
            "previous_sentence": "As with previous <unk> Chronicles games , Valkyria Chronicles III is a tactical role @-@ playing game where players take control of a military unit and take part in missions against enemy forces .",
            "marker": "and",
            "output": None
        },
        {
            ## the "that" here is not quite right, but I don't know how to resolve that the way the dependency parse works...
            "sentence": "The player progresses through a series of linear missions , gradually unlocked as maps that can be freely scanned through and replayed as they are unlocked .",
            "previous_sentence": "Stories are told through comic book @-@ like panels with animated character portraits , with characters speaking partially through voiced speech bubbles and partially through unvoiced text .",
            "marker": "and",
            "output": ('replayed as they are unlocked', 'that can be freely scanned through')
        },
        {
            ## the "where" here is not quite right, but I don't know how to resolve that the way the dependency parse works...
            "sentence": "Outside missions , the player characters rest in a camp , where units can be customized and character growth occurs .",
            "previous_sentence": "The route to each story location on the map varies depending on an individual player 's approach : when one option is selected , the other is sealed off to the player .",
            "marker": "and",
            "output": ('character growth occurs', 'where units can be customized')
        },
        # {
        #     "sentence": "",
        #     "previous_sentence": "",
        #     "marker": "and",
        #     "output": None
        # },
        # {
        #     "sentence": "",
        #     "previous_sentence": "",
        #     "marker": "",
        #     "output": None
        # }
    ]
    curious_cases = [
        {
            "sentence": "But , after inspecting the work and observing the spirit of the men I decided that a garrison 500 strong could hold out against Fitch and that I would lead the remainder - about 1500 - to Gen 'l Rust as soon as shotguns and rifles could be obtained from Little Rock instead of pikes and lances , with which most of them were armed .",
            "previous_sentence": "",
            "marker": "after",
            "output": None,
            "explanation": "incorrect parse. it thinks 'the men I decided ...' forms a relative clause. different from what's up at http://nlp.stanford.edu:8080/corenlp/process"
        },
        {
            "sentence": "In 1864 , after Little Rock fell to the Union Army and the arsenal had been recaptured , General Fredrick Steele marched 8 @,@ 500 troops from the arsenal beginning the Camden Expedition .",
            "previous_sentence": "NA",
            "marker": "after",
            "output": None
        },
        {
            "sentence": "In addition to Sega staff from the previous games , development work was also handled by <unk> The original scenario was written Kazuki Yamanobe , while the script was written by Hiroyuki Fujii , Koichi Majima , <unk> Miyagi , Seiki <unk> and Takayuki <unk> .",
            "previous_sentence": "Speaking in an interview , it was stated that the development team considered Valkyria Chronicles III to be the series ' first true sequel : while Valkyria Chronicles II had required a large amount of trial and error during development due to the platform move , the third game gave them a chance to improve upon the best parts of Valkyria Chronicles II due to being on the same platform .",
            "marker": "also",
            "output": ('while the script was written by Hiroyuki Fujii , Koichi Majima , <unk> Miyagi , Seiki <unk> and Takayuki <unk>', 'In addition to Sega staff from the previous games , development work was handled by <unk> The original scenario was written Kazuki Yamanobe , .')
        },
        ## parse is just wrong :(
        {
            "sentence": "There are also love simulation elements related to the game 's two main heroines , although they take a very minor role .",
            "previous_sentence": "After the game 's completion , additional episodes are unlocked , some of them having a higher difficulty than those found in the rest of the game .",
            "marker": "although",
            "output": ("love simulation elements related to the game 's two main heroines ,", 'they take a very minor role')
        },
        {
            "sentence": "The remainder held professional pilot licences , either a Commercial Pilot Licence or an Airline Transport Pilot Licence , although not all of these would be engaged in GA activities .",
            "previous_sentence": "The number of pilots licensed by the CAA to fly powered aircraft in 2005 was 47 @,@ 000 , of whom 28 @,@ 000 held a Private Pilot Licence .",
            "marker": "although",
            "output": ('either a Commercial Pilot Licence or an Airline Transport Pilot Licence ,', 'not all of these would be engaged in GA activities')
        },
    ]
        
    print("{} cases are weird and I can't figure out how to handle them. :(".format(len(curious_cases)))
    curious=False
    if curious:
        print("running curious cases...")
        for item in curious_cases:
            print("====================")
            print(item["sentence"])
            output = depparse_ssplit_v2(item["sentence"], item["previous_sentence"], item["marker"])
            print(output)
        print("====================")
        print("====================")
        print("====================")


    n_tests = 33
    i = 0
    failures = 0
    print("running tests...")

    for item in test_items:
        if i < n_tests:
            output = depparse_ssplit_v2(item["sentence"], item["previous_sentence"], item["marker"])
            try:
                assert(output == item["output"])
            except AssertionError:
                print("====== TEST FAILED ======" + "\nsentence: " + item["sentence"] + "\nmarker: " + item["marker"] + "\nactual output: " + str(output) + "\ndesired output: " + str(item["output"]))
                failures += 1
        else:
            print("====================")
            print(item["sentence"])
            output = depparse_ssplit_v2(item["sentence"], item["previous_sentence"], item["marker"])
            print(output)
        i += 1

    if failures==0:
        print("All tests passed.")

if __name__ == '__main__':
    args = setup_args()
    test()

