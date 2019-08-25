from PIL import Image, ImageDraw, ImageOps
import random
import pickle
import os

def save_to_file(file_name, obj):
    with open(file_name, 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_from_file(file_name):
    with open(file_name, 'rb') as f:
        return pickle.load(f)


def fitness_function(pt, pg, pm):
    fitness = 0
    if pm:
        for t, g, m in zip(pt, pg, pm):
            fitness += m*(abs(t[0] - g[0]) + abs(t[1] - g[1]) + abs(t[2] - g[2]))
    else:
        for t, g in zip(pt, pg):
            fitness += abs(t[0] - g[0]) + abs(t[1] - g[1]) + abs(t[2] - g[2])
    return fitness


def create_mask(image_size, masks):
    im = Image.new('L', image_size, 1)
    d = ImageDraw.Draw(im)
    for m in masks:
        d.rectangle(xy=m[0], fill=m[1])
    im.save('mask.png')
    return im


def draw_genome(edges, genome, size):
    im = Image.new(mode='RGB', size=size, color=(0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(0, len(genome)-2):
        d.line(xy=(edges[genome[i][0]], edges[genome[i+1][0]]), fill=(0, 0, 0), width=1)   #black
        d.line(xy=(edges[genome[i][1]], edges[genome[i+1][1]]), fill=(245, 245, 245), width=1)  #white
        d.line(xy=(edges[genome[i][2]], edges[genome[i+1][2]]), fill=(26, 82, 230), width=1) #Blue
        d.line(xy=(edges[genome[i][3]], edges[genome[i+1][3]]), fill=(255, 74, 74), width=1) #Red
        d.line(xy=(edges[genome[i][4]], edges[genome[i+1][4]]), fill=(255, 255, 108), width=1) #Yellow
    return im


def get_im_data(im, resize, crop_area):
    imR = im
    if crop_area:
        imR = im.crop(crop_area)
    imR = imR.resize(size=resize, resample=Image.LANCZOS)
    return list(imR.getdata())


def process(step, edges, genome, imt):
    resize = step['resize']
    crop_area = step['crop_area']
    mask = step['mask']

    pt = get_im_data(imt, resize, crop_area)

    pm = None
    if mask:
        im_mask = create_mask(imt.size, mask)
        pm = get_im_data(im_mask, resize, crop_area)

    img = draw_genome(edges, genome, imt.size)
    min_fitness = fitness_function(pt, pg=get_im_data(img, resize, crop_area), pm=pm)
    print("min_fitness =", min_fitness)
        
    for i in range(step['n_steps']):
        n = random.randint(0, len(genome)-1)
        ev_old = genome[n]
        
        genome[n] = [random.randint(0, len(edges)-1),
                     random.randint(0, len(edges)-1),
                     random.randint(0, len(edges)-1),
                     random.randint(0, len(edges)-1),
                     random.randint(0, len(edges)-1),
                    ]
        
        img = draw_genome(edges, genome, imt.size)
        fitness = fitness_function(pt, pg=get_im_data(img, resize, crop_area), pm=pm)
        if i % 1000 == 0:
            print(i, 'min=', min_fitness)
        if fitness < min_fitness:
            min_fitness = fitness
        else:
            genome[n] = ev_old

    return min_fitness 

def main(imt, edges, steps, genome_file_name=None, genome_size=None):
    os.makedirs('gen', exist_ok=True)

    if genome_file_name:
        genome = load_from_file(genome_file_name)
    else:
        if genome_size and genome_size > 0:
            genome = [[random.randint(0, len(edges)-1), 
                       random.randint(0, len(edges)-1),
                       random.randint(0, len(edges)-1),
                       random.randint(0, len(edges)-1),
                       random.randint(0, len(edges)-1),
                     ] for i in range(genome_size)]      
        else:
            raise ValueError('genome size is not defined')

    for i, st in enumerate(steps):
        print("step=", i)
        fitness = process(st, edges, genome, imt)
        save_to_file("gen/"+str(i)+'_'+str(fitness)+'.gen', genome)
        img = draw_genome(edges, genome, imt.size)
        img.save("gen/"+str(i)+'_'+str(fitness)+'.png')


if __name__ == "__main__":
    file_name = 'Girl with a Pearl Earring.jpg'
    im = Image.open(file_name).                               \
               crop(box=(530, 350, 580+3650, 400+3650)).      \
               resize(size=(512, 512), resample=Image.LANCZOS)      
    im.save(file_name+'_original.png')

    edges = []
    for i in range(0, 512+16, 16):
        edges.append((0, i))
        edges.append((512, i))
    for i in range(16, 512, 16):
        edges.append((i, 512))
        edges.append((i, 0))
 
    steps = [
       {
         'n_steps': 200000,
         'resize': (32, 32),
         'crop_area': (102, 154, 102+209, 154+209),
         'mask': None,
       },
 
       {
         'n_steps': 250000,
         'resize': (32, 32),
         'crop_area': (92, 144, 92+229, 144+229),
         'mask': None,      
       },

       {
         'n_steps': 350000,
         'resize': (34, 34),
         'crop_area': (82, 134, 82+249, 134+249),
         'mask': None,      
       },

       {
         'n_steps': 400000,
         'resize': (34, 34),
         'crop_area': (72, 124, 72+269, 124+269),
         'mask': None,      
       },

       {
         'n_steps': 400000,
         'resize': (36, 36),
         'crop_area': (62, 114, 62+289, 114+289),
         'mask': None,      
       },

       {
         'n_steps': 400000,
         'resize': (38, 38),
         'crop_area': (52, 104, 52+309, 104+309),
         'mask': None,      
       },
        
       {
         'n_steps': 400000,
         'resize': (40, 40),
         'crop_area': None,
         'mask': None,      
       },
       
   ]

    main(im, edges, steps, 
         genome_file_name=None, 
         genome_size=1000)
