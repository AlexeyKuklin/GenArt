from PIL import Image, ImageDraw, ImageOps
import random
import pickle

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
            fitness = fitness + m*abs(t - g)
    else:
        for t, g in zip(pt, pg):
            fitness = fitness + abs(t - g)
            #fitness = fitness + abs(t[0] - g[0]) + abs(t[1] - g[1]) + abs(t[2] - g[2])

    return fitness

def open_mask(file_name):
    im = Image.open(file_name)
    im = ImageOps.grayscale(image=im)
    pd = im.load()
    for i in range(im.size[0]): # for every pixel:
        for j in range(im.size[1]):
            if pd[i, j] == 0:
                pd[i, j] = 1
    im.save(file_name+'_mask.png')
    return im

def draw_genome(edges, genome, size):
    im = Image.new(mode='RGB', size=size, color=(255, 255, 255))
    d = ImageDraw.Draw(im)
    for i in range(len(genome)-2):
        d.line(xy=(edges[genome[i][0]], edges[genome[i+1][0]]), fill=(0, 0, 0), width=1)
        #d.line(xy=(edges[genome[i][1]], edges[genome[i+1][1]]), fill=(255, 255, 255, 50), width=1)
    im = ImageOps.grayscale(image=im) ###
    return im

def process(n_steps, edges, genome, imt, mask):
    pt = list(imt.getdata())    
    pm = None
    if mask:
        pm = list(mask.getdata())

    img = draw_genome(edges, genome, imt.size)
    pg = list(img.getdata())
    min_fitness = fitness_function(pt, pg, pm)
    print("min_fitness =", min_fitness)
        
    for i in range(n_steps):
        n = random.randint(0, len(genome)-1)
        ev_old = genome[n][0]
        genome[n][0] = random.randint(0, len(edges)-1)

        img = draw_genome(edges, genome, imt.size)
        pg = list(img.getdata())

        fitness = fitness_function(pt, pg, pm)
        if fitness < min_fitness:
            min_fitness = fitness
            print(i, '=', fitness)
            img.save("gen/"+str(i)+'_'+str(fitness)+'.png')
            save_to_file("gen/"+str(i)+'_'+str(fitness)+'.gen', genome)
        else:
            genome[n][0] = ev_old

def main(imt, edges, n_steps, genome_file_name=None, genome_size=None, mask_file_name=None):
    if genome_file_name:
        genome = load_from_file(genome_file_name)
    else:
        if genome_size and genome_size > 0:
            genome = [[random.randint(0, len(edges)-1), 
                       random.randint(0, len(edges)-1)
                     ] for i in range(genome_size)]      
            #genome = [[0, 0] for i in range(genome_size)]      
        else:
            raise ValueError('genome size is not defined')

    mask = None
    if mask_file_name:
        mask = open_mask(file_name=mask_file_name)

    process(n_steps, edges, genome, imt, mask)

if __name__ == "__main__":
    file_name = 'Girl with a Pearl Earring.jpg'
    im = Image.open(file_name)
    im = ImageOps.grayscale(image=im)
    rgbimg = Image.new("RGB", im.size)
    rgbimg.paste(im)
    im = rgbimg
    area = (700, 500, 700+3100, 500+3100)
    size = (512, 512)

    im = ImageOps.grayscale(image=im) ###
    im = im.crop(area).resize(size, Image.LANCZOS)
    im.save(file_name+'_original.png')

    edges = []
    for i in range(16, 512, 16):
        edges.append((0, i))
        edges.append((512, i))
        edges.append((i, 512))
        edges.append((i, 0))
 
    main(im, edges, 2000000, genome_size=1000)
