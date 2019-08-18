from PIL import Image, ImageDraw, ImageOps
import random

def get_edges():
    edges = []
    for i in range(16, 512, 16):
        edges.append((0, i))
        edges.append((512, i))
        edges.append((i, 512))
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
    im = ImageOps.fit(image=im, size=(512, 512), method=0, bleed=0.0, centering=(0.5, 0.5))
    im = ImageOps.grayscale(image=im)
    im.save(file_name+'_original.png')
    return im

def draw_genome(genome):
    im = Image.new(mode='RGB', size=(512, 512), color=(255, 255, 255))
    im = ImageOps.grayscale(image=im)
    d = ImageDraw.Draw(im)
    d.line(xy=[edges[g] for g in genome], fill=0, width=1)
    return im

edges = get_edges()
genome = [random.randint(0, len(edges)-1) for i in range(1000)]

imt = open_original_image(file_name="1.jpg")
img = draw_genome(genome)
min_fitness = fitness_function(imt, img)
print(-1, '=', min_fitness)

cnt = 0
for i in range(500000):
    new_genome = list(genome)
    new_genome[random.randint(0, len(genome)-1)] = random.randint(0, len(edges)-1)
    img = draw_genome(new_genome)

    fitness = fitness_function(imt, img)
    if fitness < min_fitness:
        min_fitness = fitness
        genome = new_genome
        print(i, '=', fitness)
        cnt += 1
        if cnt % 10 == 0:
            img.save("gen/"+'step_'+str(i)+'_fit_'+str(fitness)+'.png')

img = draw_genome(genome)
img.save('result.png')



