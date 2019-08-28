from PIL import Image, ImageDraw, ImageOps
import random
import pickle
import os
import math


def save_to_file(file_name, obj):
    with open(file_name, 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_from_file(file_name):
    with open(file_name, 'rb') as f:
        return pickle.load(f)


def fitness_function(pt, pg, pm):
    fitness = 0
    for t, g, m in zip(pt, pg, pm):
        if m > 0:
            fitness += m*(abs(t[0] - g[0]) + abs(t[1] - g[1]) + abs(t[2] - g[2]))
        #fitness += abs(t[0] - g[0]) + abs(t[1] - g[1]) + abs(t[2] - g[2])
    return fitness


def create_mask(image_size, masks):
    im = Image.new('L', image_size, 1)
    d = ImageDraw.Draw(im)
    if masks:
        for m in masks:
            d.rectangle(xy=m[0], fill=m[1])
    im.save('mask.png')
    return im


def draw_genome(edges, genome, size, genome_range):
    im = Image.new(mode='RGB', size=size, color=(0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(genome_range[0], genome_range[1]-1):
        d.line(xy=(edges[genome[i][0]], edges[genome[i+1][0]]), fill=(0, 0, 0), width=1)   #black
        d.line(xy=(edges[genome[i][1]], edges[genome[i+1][1]]), fill=(245, 245, 245), width=1)  #white
        d.line(xy=(edges[genome[i][2]], edges[genome[i+1][2]]), fill=(26, 82, 230), width=1) #Blue
        d.line(xy=(edges[genome[i][3]], edges[genome[i+1][3]]), fill=(255, 74, 74), width=1) #Red
        d.line(xy=(edges[genome[i][4]], edges[genome[i+1][4]]), fill=(255, 255, 108), width=1) #Yellow
    return im


def get_im_data(im, resize):
    imR = im.resize(size=resize, resample=Image.LANCZOS)
    return list(imR.getdata())


def process(step, edges, genome, imt):
    print("step=", step['n'])

    resize = step['resize']
    mask = step['mask']
    draw_genome_range = step['draw_genome_range']
    opt_genome_range = step['opt_genome_range']

    if draw_genome_range is None:
        draw_genome_range = (0, len(genome)-1)

    if opt_genome_range is None:
        opt_genome_range = (0, len(genome)-1)

    pt = get_im_data(imt, resize)

    im_mask = create_mask(imt.size, mask)
    pm = get_im_data(im_mask, resize)

    img = draw_genome(edges, genome, imt.size, draw_genome_range)
    min_fitness = fitness_function(pt, pg=get_im_data(img, resize), pm=pm)
    print("min_fitness =", min_fitness)
    min_min_fitness = min_fitness
    
    for i in range(step['n_steps']):
        n = random.randint(opt_genome_range[0], opt_genome_range[1])
        ev_old = genome[n]

        k = random.randint(0, 6)
        if k == 0:
            genome[n] = [random.randint(0, len(edges)-1),
                        genome[n][1],
                        genome[n][2],
                        genome[n][3],
                        genome[n][4]]  
        elif k == 1:
            genome[n] = [genome[n][0],
                        random.randint(0, len(edges)-1),
                        genome[n][2],
                        genome[n][3],
                        genome[n][4]]
        elif k == 2:
            genome[n] = [genome[n][0],
                        genome[n][1],
                        random.randint(0, len(edges)-1),
                        genome[n][3],
                        genome[n][4]]
        elif k == 3:
            genome[n] = [genome[n][0],
                        genome[n][1],
                        genome[n][2],
                        random.randint(0, len(edges)-1),
                        genome[n][4]]
        elif k == 4:
            genome[n] = [genome[n][0],
                         genome[n][1],
                         genome[n][2],
                         genome[n][3],
                         random.randint(0, len(edges)-1)]
        else:
            genome[n] = [random.randint(0, len(edges)-1),
                         random.randint(0, len(edges)-1),
                         random.randint(0, len(edges)-1),
                         random.randint(0, len(edges)-1),
                         random.randint(0, len(edges)-1)]

        img = draw_genome(edges, genome, imt.size, draw_genome_range)
        fitness = fitness_function(pt, pg=get_im_data(img, resize), pm=pm)
        if i % 1000 == 0:
            print(i, 'min=', min_fitness, '%=', min_fitness/min_min_fitness*100)
        if fitness < min_fitness:
            min_fitness = fitness
        else:
            genome[n] = ev_old

    print(step['n_steps'], 'min=', min_fitness, '%=', min_fitness/min_min_fitness*100)
    img = draw_genome(edges, genome, imt.size, draw_genome_range)
    img.save("gen/"+str(step['n'])+'_'+str(min_fitness)+'.png')
    save_to_file("gen/"+str(step['n'])+'_'+str(min_fitness)+'.gen', genome)


def main(imt, edges, steps, genome_file_name=None, genome_size=None):
    if genome_file_name:
        genome = load_from_file(genome_file_name)
    else:
        if genome_size and genome_size > 0:
            genome = [[random.randint(0, len(edges)-1) for i in range(5)] for i in range(genome_size)]      
        else:
            raise ValueError('genome size is not defined')

    for st in steps:
        process(st, edges, genome, imt)


if __name__ == "__main__":
    random.seed(42)
    os.makedirs('gen', exist_ok=True)

    file_name = 'Girl with a Pearl Earring.jpg'
    im = Image.open(file_name).                               \
               crop(box=(530, 350, 580+3650, 400+3650)).      \
               resize(size=(512, 512), resample=Image.LANCZOS)      
    im.save(file_name+'_original.png')

    edges = []
    #d = ImageDraw.Draw(im) 
    for i in range(0, 360, 2):
        x = 256*math.cos(math.radians(i))
        y = 256*math.sin(math.radians(i))
        edges.append((256+x, 256+y))
        #d.line(xy=(256, 256, 256+x, 256+y), fill=(255, 74, 74), width=1)
    #im.save(file_name+'_original.png')

    steps = [
       {
         'n': 0,
         'n_steps': 200000,
         'resize': (32, 32),
         'opt_genome_range': (0, 999),
         'draw_genome_range': (0, 999),
         'mask': [((102, 154, 102+209, 154+209), 2)]
       },
    ]

    main(im, edges, steps, 
         genome_file_name='gen/0_61234.gen', 
         genome_size=1000)     
 