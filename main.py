from PIL import Image, ImageDraw, ImageOps
import random
import pickle

IMG_SIZE = 512

def save_to_file(file_name, obj):
    with open(file_name, 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_from_file(file_name):
    with open(file_name, 'rb') as f:
        return pickle.load(f)

def get_edges():
    edges = []
    for i in range(16, IMG_SIZE, 16):
        edges.append((0, i))
        edges.append((IMG_SIZE, i))
        edges.append((i, IMG_SIZE))
        edges.append((i, 0))
    return edges

def fitness_function(pt, pg, pm):
    fitness = 0
    #fitness = fitness + abs(t[0] - g[0]) + abs(t[1] - g[1]) + abs(t[2] - g[2])
    if pm:
        for t, g, m in zip(pt, pg, pm):
            fitness = fitness + m*abs(t - g)
    else:
        for t, g in zip(pt, pg):
            fitness = fitness + abs(t - g)

    return fitness

def open_original_image(file_name):
    im = Image.open(file_name)
    im = ImageOps.fit(image=im, size=(IMG_SIZE, IMG_SIZE), method=0, bleed=0.0, centering=(0.5, 0.5))
    im = ImageOps.grayscale(image=im)
    im.save(file_name+'_original.png')
    return im

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

def draw_genome(edges, genome):
    im = Image.new(mode='RGB', size=(IMG_SIZE, IMG_SIZE), color=(255, 255, 255))
    im = ImageOps.grayscale(image=im)
    d = ImageDraw.Draw(im)
    d.line(xy=[edges[g] for g in genome], fill=0, width=1)
    return im

def process(n_steps, edges, genome, imt, mask):
    pt = list(imt.getdata())    
    pm = None
    if mask:
        pm = list(mask.getdata())

    img = draw_genome(edges, genome)
    pg = list(img.getdata())
    min_fitness = fitness_function(pt, pg, pm)
    print("min_fitness =", min_fitness)
        
    for i in range(n_steps):
        new_genome = list(genome)
        new_genome[random.randint(0, len(genome)-1)] = random.randint(0, len(edges)-1)
        img = draw_genome(edges, new_genome)
        pg = list(img.getdata())

        fitness = fitness_function(pt, pg, pm)
        if fitness < min_fitness:
            min_fitness = fitness
            genome = new_genome
            print(i, '=', fitness)
            img.save("gen/"+str(i)+'_'+str(fitness)+'.png')
            save_to_file("gen/"+str(i)+'_'+str(fitness)+'.gen', genome)


def main(n_steps, original_file_name, genome_file_name=None, genome_size=None, mask_file_name=None):
    imt = open_original_image(file_name=original_file_name)
    if genome_file_name:
        genome = load_from_file(genome_file_name)
    else:
        if genome_size > 0:
            genome = [random.randint(0, len(edges)-1) for i in range(genome_size)]      
        else:
            raise ValueError('genome size is not defined')

    mask = None
    if mask_file_name:
        mask = open_mask(file_name=mask_file_name)

    edges = get_edges()
    process(n_steps, edges, genome, imt, mask)

if __name__ == "__main__":
    main(1000000, 'Girl with a Pearl Earring.jpg')

