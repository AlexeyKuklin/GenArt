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

def fitness_function(imt, img):
    pt = list(imt.getdata())
    pg = list(img.getdata())

    fitness = 0
    for t, g in zip(pt, pg):
        #fitness = fitness + abs(t[0] - g[0]) + abs(t[1] - g[1]) + abs(t[2] - g[2])
        fitness = fitness + abs(t - g)
    return fitness

def open_original_image(file_name):
    im = Image.open(file_name)
    im = ImageOps.fit(image=im, size=(IMG_SIZE, IMG_SIZE), method=0, bleed=0.0, centering=(0.5, 0.5))
    im = ImageOps.grayscale(image=im)
    im.save(file_name+'_original.png')
    return im

def draw_genome(edges, genome):
    im = Image.new(mode='RGB', size=(IMG_SIZE, IMG_SIZE), color=(255, 255, 255))
    im = ImageOps.grayscale(image=im)
    d = ImageDraw.Draw(im)
    d.line(xy=[edges[g] for g in genome], fill=0, width=1)
    return im

def process(n_steps, edges, genome):
    imt = open_original_image(file_name="1.jpg")
    img = draw_genome(edges, genome)
    min_fitness = fitness_function(imt, img)
    print('min_fitness =', min_fitness)

    cnt = 0
    for i in range(n_steps):
        new_genome = list(genome)
        new_genome[random.randint(0, len(genome)-1)] = random.randint(0, len(edges)-1)
        img = draw_genome(edges, new_genome)

        fitness = fitness_function(imt, img)
        if fitness < min_fitness:
            min_fitness = fitness
            genome = new_genome
            print(i, '=', fitness)
            if cnt % 10 == 0:
                img.save("gen/"+str(i)+'_'+str(fitness)+'.png')
                save_to_file("gen/"+str(i)+'_'+str(fitness)+'.gen', genome)

    img.save("gen/"+str(n_steps)+'_'+str(fitness)+'.png')
    save_to_file("gen/"+str(n_steps)+'_'+str(fitness)+'.gen', genome)

def main(genome_file_name):
    edges = get_edges()
    if genome_file_name:
        genome = load_from_file(genome_file_name)
    else:
        genome = [random.randint(0, len(edges)-1) for i in range(1000)]
    process(100000, edges, genome)

if __name__ == "__main__":
    main(None)
