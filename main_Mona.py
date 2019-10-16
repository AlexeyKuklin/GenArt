from PIL import Image, ImageDraw, ImageOps
import random
import datetime as dt
import pickle
import os
import math
#import numpy as np

class Optimizer:
    def __init__(self, genome_file_name=None, imt=None, genome_size=None, colors=None, edge_form='circle', edge_step=None):
        self.genome_file_name = genome_file_name
        self.genome_size = genome_size
        self.genome = None
        self.colors = colors
        self.edges = []
        self.imt = imt

        if self.genome_file_name:
            self.load_from_file(genome_file_name)
            #self.imt.save('_original.png')
        else:
            self.set_edges(form=edge_form, step=edge_step)
            if genome_size and genome_size > 0:
                self.genome = [[random.randint(0, len(self.edges)-1) for i in range(len(self.colors))] for i in range(self.genome_size)]      
            else:
                raise ValueError('genome size is not defined')

    def save_to_file(self, file_name):
        with open(file_name, 'wb') as f:
            obj = [self.genome, self.colors, self.edges, self.imt]
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_from_file(self, file_name):
        with open(file_name, 'rb') as f:
            obj = pickle.load(f)
            self.genome = obj[0]
            self.colors = obj[1]
            self.edges = obj[2]
            self.imt = obj[3]
            self.genome_size = len(self.genome)

    def set_edges(self, form, step):
        width, height = self.imt.size   
        if form == 'square':
            for i in range(0, height+step, step):
                self.edges.append((0, i))
                self.edges.append((height, i))
            for i in range(step, width, step):
                self.edges.append((i, width))
                self.edges.append((i, 0))
        elif form == 'circle':
            for i in range(0, 360, step):
                x = (width/2)*math.cos(math.radians(i))
                y = (height/2)*math.sin(math.radians(i))
                self.edges.append(((width/2)+x, (height/2)+y))

    def create_mask(self, image_size, masks):
        im = Image.new('L', image_size, 1)
        if masks:
            d = ImageDraw.Draw(im)
            for m in masks:
                d.rectangle(xy=m[0], fill=m[1])
        im.save('mask.png')
        return im

    #def transform_genome():
    #    for g in self.genome:
    #        g1 = g.copy()
    #        for i in 

    def draw_genome(self, genome_range):
        im = Image.new(mode='RGB', size=self.imt.size, color=(0, 0, 0))
        d = ImageDraw.Draw(im)
        for i in range(genome_range[0], genome_range[1]-1):
            for j, c in enumerate(self.colors):
                if c:
                    d.line(xy=(self.edges[self.genome[i][j]], self.edges[self.genome[i+1][j]]), fill=c, width=1)   
        return im

    def get_im_data(self, im, resize):
        imR = im.resize(size=resize, resample=Image.LANCZOS)
        return list(imR.getdata())

    def fitness_function(self, pt, pg, pm):
        
        fitness = 0
        for t, g, m in zip(pt, pg, pm):
            if m > 0:
                fitness += m*(abs(t[0] - g[0]) + abs(t[1] - g[1]) + abs(t[2] - g[2]))
        #for t, g in zip(pt, pg):
        #    fitness += (abs(t[0] - g[0]) + abs(t[1] - g[1]) + abs(t[2] - g[2]))
        """
        d = 0
        for i in range(0, 999-1):
            for j, c in enumerate(self.colors):
                if c:
                    d += math.pow(self.edges[self.genome[i][j]][0]-self.edges[self.genome[i+1][j]][0], 2) + \
                    math.pow(self.edges[self.genome[i][j]][1]-self.edges[self.genome[i+1][j]][1], 2)

        fitness += 0.0001*d
        """
        return fitness

    def print_time(self, step_n, min_fitness, min_min_fitness, t0):
        print('step={}, min={}, opt%={}, time={}'.format(
               step_n,  min_fitness, min_fitness/min_min_fitness*100,
               str(dt.timedelta(seconds=(dt.datetime.now()-t0).total_seconds()))[:-7]))

    def process(self, step):
        print("step=", step['n'])

        resize = step['resize']
        mask = step['mask']
        draw_genome_range = step['draw_genome_range']
        opt_genome_range = step['opt_genome_range']
        max_colors = len(self.colors)

        if draw_genome_range is None:
            draw_genome_range = (0, len(genome)-1)

        if opt_genome_range is None:
            opt_genome_range = (0, len(genome)-1)

        pt = self.get_im_data(self.imt, resize)

        im_mask = self.create_mask(self.imt.size, mask)
        pm = self.get_im_data(im_mask, resize)

        img = self.draw_genome(draw_genome_range)
        min_fitness = self.fitness_function(pt, pg=self.get_im_data(img, resize), pm=pm)
        min_min_fitness = min_fitness


        #img = self.draw_genome(draw_genome_range)
        #img.save('gen/test4.png')
        #exit()
    
        t0 = dt.datetime.now()       
        for i in range(step['n_steps']):
            n = random.randint(opt_genome_range[0], opt_genome_range[1])
            ev_old = self.genome[n].copy()

            k = random.randint(0, len(self.colors))
            if k < len(self.colors): 
                self.genome[n][k] = random.randint(0, len(self.edges)-1)
            else:
                self.genome[n] = [random.randint(0, len(self.edges)-1) for j in range(len(self.colors))]

            img = self.draw_genome(draw_genome_range)
            fitness = self.fitness_function(pt, pg=self.get_im_data(img, resize), pm=pm)
            if i % 1000 == 0:
                self.print_time(i, min_fitness, min_min_fitness, t0)
                if i % 50000 == 0:
                    img = self.draw_genome(draw_genome_range)
                    img.save("gen/"+str(min_fitness)+'.png')
                    self.save_to_file("gen/"+str(min_fitness)+'.gen')
            if fitness < min_fitness:
                min_fitness = fitness
            else:
                self.genome[n] = ev_old

        self.print_time(step['n_steps'], min_fitness, min_min_fitness, t0)
        img = self.draw_genome(draw_genome_range)
        img.save("gen/"+str(step['n'])+'_'+str(min_fitness)+'.png')
        self.save_to_file("gen/"+str(min_fitness)+'.gen')


    def main(self, steps):
        for st in steps:
            self.process(st)

#'mask': [((225, 284, 225+505, 284+480), 3), ((0, 0, 180, 1024), 0), ((900, 0, 1024, 1024), 0), ((788, 0, 788+236, 393), 0)] 
#[((225, 284, 225+505, 284+480), 3)]

if __name__ == "__main__":
    random.seed(42)
    os.makedirs('gen', exist_ok=True)
    op = None

    genome_file_name = None
    #genome_file_name='gen/0_625778.gen' #626575.gen'
    if genome_file_name:
        op = Optimizer(genome_file_name=genome_file_name)
    else:
        file_name = 'Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched.jpg'
        imt = Image.open(file_name).                                  \
                    crop(box=(1689, 1001, 1689+4250, 1101+4250)).      \
                    resize(size=(1024, 1024), resample=Image.LANCZOS)      
        imt.save(file_name+'_original.png')

        colors = [(0, 0, 0),         #black
                  (245, 245, 245),   #white
                  (24, 126, 55),    #green
                  (255, 74, 74),    #red
                  (255, 255, 108)   #yellow
                 ]  

        op = Optimizer(genome_size=1000,
                       imt=imt,
                       colors=colors,
                       edge_form='circle',
                       edge_step=2
                      )

    steps = [
       {
         'n': 0,
         'n_steps': 10000000,
         'resize': (96, 96),
         'opt_genome_range': (0, 999),
         'draw_genome_range': (0, 999),
         'mask': [((245, 150, 245+420, 150+554), 3)] 
       },
    ]
    op.main(steps)     
 
