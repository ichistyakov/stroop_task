# -*- coding: utf-8 -*-
from __future__ import division
import operator  # Allows to pass object attribute as parameter
import pandas  # Required for more native navigation through CSV files
import itertools  # Useful to check schedule of reinforcement and change phases
from ast import literal_eval  # Required to read color values from CSV files
import os
# PyGame
import pygame
# Custom classes
import config as c  # Configuration file
from text_object import TextObject
from button import Button
import colors  # Colors list
# Math
from math import log, exp


class Stroop(Game):

    # Constructor
    def __init__(self):
        Game.__init__(self, 'Stimulus control competition task', c.background_image, c.frame_rate)
        # Loads experimental setup
        self.df = pandas.read_csv(c._thisDir + os.sep + 'stimuli' + os.sep + c.setup,
                                  encoding="utf-8"
                                  )
        # Creates iterator to loop over phases
        self.phases = itertools.cycle(self.df['phase'].unique())
        self.phase = self.phases.next()
        # Constructs counters
        self.score = 0
        self.counters = []
        self.counters.append(TextObject(
                                 0.06*w, 0.06*h,
                                 lambda: u'Счет: %i' %self.score,
                                 colors.WHITE, c.font_name, int(c.font_size*h)
                                )
                             )
        # Constructs stimuli
        self.stimuli = []
        self.stimuli.append(TextStimulus(
                                0.35*w, 0.45*h,
                                self.df.loc[self.df['phase'] == self.phase].sample(1),
                                c.font_name, int(c.font_size*h)
                                )
                            )
        self.stimuli.append(TextStimulus(
                                0.65*w, 0.45*h,
                                self.df.loc[self.df['phase'] == self.phase].sample(1),
                                c.font_name, int(c.font_size*h)
                                )
                            )
        # Initializes event to change stimuli every n seconds
        self.rate = 1
        self.CHANGE_STIMULI = pygame.USEREVENT + 1
        # Constructs necessary buttons
        self.buttons = []
        self.buttons.append(Button(
                            0.5*w - 0.15*w // 2,
                            0.85*h - 0.15*h // 2, 0.15*w, 0.15*h,
                            on_click=lambda x: self.handle_reinforcement(are_stimuli_equal(iter(self.stimuli),
                                                                                           attr='label'),
                                                                         reinforcement=1)
                                   )
                            )
        pygame.time.set_timer(self.CHANGE_STIMULI, int(1000 / self.rate))
        # Finishes initialization
        self.screen.fill(self.bg)
        self.clock = pygame.time.Clock()
        print 'Session started!'

    # Updates the game
    def update(self):
        self.handle_events()
        self.clock.tick(self.fps)
        self.screen.fill(self.bg)
        for b in self.buttons:
            b.draw(self.screen)
        for c in self.counters:
            c.draw(self.screen, False)
        for s in self.stimuli:
            s.stimulus.draw(self.screen, True)
        pygame.display.flip()

    # Checks whether the user has clicked to exit (required to avoid crash)
    def handle_events(self):
        # Checks if the user exited
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print 'Session finished!'
                    exit()
                if event.key == pygame.K_q:
                    self.phase = self.phases.next()
            if event.type == self.CHANGE_STIMULI:
                for s in self.stimuli:
                    s.update(self.df.loc[self.df['phase'] == self.phase].sample(1))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4 or event.button == 5:
                    if event.button == 4:
                        # Logarithmic scale prevents negative values
                        self.rate = exp(log(self.rate)+0.01)
                    if event.button == 5:
                        self.rate = exp(log(self.rate)-0.01)
                    pygame.time.set_timer(self.CHANGE_STIMULI, int(1000 / self.rate))
            for b in self.buttons:
                b.handle_mouse_event(event.type, pygame.mouse.get_pos())

    # Defines schedule of reinforcement
    def handle_reinforcement(self, event, reinforcement):
        if event:
            self.score += reinforcement
        else:
            self.score -= reinforcement


class TextStimulus(object):

    def __init__(self, x, y, contents, font_name, font_size):
        self.text = contents['text'].item()
        self.label = contents['label'].item()
        self.color = literal_eval(contents['color'].item())
        self.stimulus = TextObject(
        x, y, lambda: self.text,
        self.color, font_name, font_size
        )

    def update(self, new_contents):
        self.text = new_contents['text'].item()
        self.label = new_contents['label'].item()
        self.stimulus.color = literal_eval(new_contents['color'].item())


# Checks whether stimuli are equal
def are_stimuli_equal(iterator, attr):
    attr = operator.attrgetter(attr)
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(attr(first) == attr(rest) for rest in iterator)


# If the file was run and not imported
if __name__ == "__main__":


    # Creates the game object
    game = Game()
    # Every tick updates the game
    while True:
        game.update()
