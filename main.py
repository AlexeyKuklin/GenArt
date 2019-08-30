from PIL import Image, ImageDraw, ImageOps
import random
import pickle
import os
import math

class Optimizer:
    def __init__(self, genome_file_name=None, genome_size=None):
        self.genome_file_name = genome_file_name
        self.genome_size = genome_size
        self.genome = None
        self.colors = None
        self.edges = []
        self.imt = None

        if self.genome_file_name:
            self.load_from_file(genome_file_name)
            self.imt.save('_original.png')
        else:
            file_name = 'Girl with a Pearl Earring.jpg'
            self.imt = Image.open(file_name).                         \
                       crop(box=(530, 350, 580+3650, 400+3650)).      \
                       resize(size=(512, 512), resample=Image.LANCZOS)      
            self.imt.save(file_name+'_original.png')

            self.colors = [(0, 0, 0), #black
                  (245, 245, 245),  #white
                  (26, 82, 230),    #Blue
                  (255, 74, 74),    #Red
                  (255, 255, 108)]  #Yellow

            self.get_edges('circle', self.imt.size, 2) #(form, size, step)
            if genome_size and genome_size > 0:
                self.genome = [[random.randint(0, len(self.edges)-1) for i in range(5)] for i in range(self.genome_size)]      
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
            self.genome_size = len(self.genome)
            self.colors = obj[1]
            self.edges = obj[2]
            self.imt = obj[3]

    def get_edges(self, form, size, step):
        width, height = size   
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

    def draw_genome(self, genome_range):
        im = Image.new(mode='RGB', size=self.imt.size, color=(0, 0, 0))
        d = ImageDraw.Draw(im)
        for i in range(genome_range[0], genome_range[1]-1):
            for j, c in enumerate(self.colors):
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
        return fitness

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
        print("min_fitness =", min_fitness)
        min_min_fitness = min_fitness
    
        for i in range(step['n_steps']):
            n = random.randint(opt_genome_range[0], opt_genome_range[1])
            ev_old = self.genome[n].copy()

            k = random.randint(0, 5)
            if k < 5: 
                self.genome[n][k] = random.randint(0, len(self.edges)-1)
            else:
                self.genome[n] = [random.randint(0, len(self.edges)-1) for j in range(5)]

            img = self.draw_genome(draw_genome_range)
            fitness = self.fitness_function(pt, pg=self.get_im_data(img, resize), pm=pm)
            if i % 1000 == 0:
                print(i, 'min=', min_fitness, '%=', min_fitness/min_min_fitness*100)
            if fitness < min_fitness:
                min_fitness = fitness
            else:
                self.genome[n] = ev_old

        print(step['n_steps'], 'min=', min_fitness, '%=', min_fitness/min_min_fitness*100)
        img = self.draw_genome(draw_genome_range)
        img.save("gen/"+str(step['n'])+'_'+str(min_fitness)+'.png')
        self.save_to_file("gen/"+str(step['n'])+'_'+str(min_fitness)+'.gen')


    def main(self, steps):
        for st in steps:
            self.process(st)


if __name__ == "__main__":
    random.seed(42)
    os.makedirs('gen', exist_ok=True)
    steps = [
       {
         'n': 0,
         'n_steps': 4500000,
         'resize': (64, 64),
         'opt_genome_range': (0, 999),
         'draw_genome_range': (0, 999),
         'mask': [((102, 154, 102+209, 154+209), 10)]
       },
    ]
    op = Optimizer(#genome_file_name='gen/0_688970.gen',
                   genome_size=1000)
    op.main(steps)     
