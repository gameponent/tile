#!/usr/bin/env python

from gimpfu import register, PF_IMAGE, PF_FILE, pdb, main
import Image
import json
import os
import tempfile
import uuid
import pystache

TEMP_DIR = os.path.join(tempfile.gettempdir(), 'tile_exporter')

def upper_camel_case(txt):
    return ''.join([word.capitalize() for word in txt.split(' ')])

def lower_snake_case(txt):
    return '_'.join([word.lower() for word in txt.split(' ')])

def upper_snake_case(txt):
    return '_'.join([word.upper() for word in txt.split(' ')])

def lower_case(txt):
    return ''.join([word.lower() for word in txt.split(' ')])

def make_directory(dirname):
    try:
        os.makedirs(dirname)
    except:
        pass
    return dirname

def create_temp_directory():
    return make_directory(os.path.join(TEMP_DIR, str(uuid.uuid1())))

def create_tile_directory(img):
    return make_directory(os.path.abspath(os.path.join(
        os.path.dirname(img.filename), 'tilesets'
    )))

def export_animation(img, animation_group, tileset_group):
    frames = []
    animation = {
        'name': animation_group.name,
        'frames': frames,
        'constant': upper_snake_case(animation_group.name),
        'class': upper_camel_case(animation_group.name),
        'fps': 20
    }
    tempdir = create_temp_directory()
    animation_layers = [animation_group]
    if animation_group.children:
        animation_layers = animation_group.children
    for frame_layer in animation_layers:
        file_name = os.path.join(tempdir, frame_layer.name + '.png')
        pdb.gimp_file_save(img, frame_layer, file_name, file_name)
        image = Image.open(file_name)
        frames.append({'image': image, 'animation': animation})
    return animation

def append_chunk_to_line(chunk, line):
    image = chunk['image']
    image_width, image_height = image.size
    line['chunks'].append(chunk)
    line['width'] += image_width
    line['height'] = max(image_height, line['height'])

def get_chunks_lines(chunks):
    chunks_lines = []
    width_total = sum(c['image'].size[0] for c in chunks)
    width_max = width_total / 3
    line = None
    for chunk in chunks:
        image = chunk['image']
        image_width, image_height = image.size
        if line is None or line['width'] + image_width > width_max:
            line = {'width': 0, 'height': 0, 'chunks': []}
            chunks_lines.append(line)
        append_chunk_to_line(chunk, line)
    return chunks_lines

def print_tileset(chunks_lines, path):
    width = max(l['width'] for l in chunks_lines)
    height = sum(l['height'] for l in chunks_lines)
    tileset = Image.new('RGBA', (width, height))
    y = 0
    for line in chunks_lines:
        x = 0
        for chunk in line['chunks']:
            image = chunk['image']
            chunk['x'] = x
            chunk['y'] = y
            chunk['width'] = image.size[0]
            chunk['height'] = image.size[1]
            tileset.paste(image, (x, y))
            x += image.size[0]
        y += line['height']
    tileset.save(path)

def export_json_data(tileset_group, animations, json_data):
    json_data['tilesets'].append({
        'name': lower_snake_case(tileset_group.name),
        'groups': [{
            'name': a['name'],
            'infos': {'fps': a['fps']},
            'tiles': [{
                'name': '%s_%d' % (a['name'], a['frames'].index(f)),
                'x': f['x'],
                'y': f['y'],
                'width': f['width'],
                'height': f['height']
            } for f in a['frames']]
        } for a in animations]
    })

def export_tileset(img, tiles_dir, tileset_group, json_data):
    chunks = []
    animations = []
    for animation_group in tileset_group.children:
        animation = export_animation(img, animation_group, tileset_group)
        chunks.extend(animation['frames'])
        animations.append(animation)
    chunks_lines = get_chunks_lines(chunks)
    print_tileset(chunks_lines, os.path.join(tiles_dir, lower_snake_case(tileset_group.name)) + '.png')
    export_json_data(tileset_group, animations, json_data)

def export_tilesets(img) :
    json_data = {'tilesets': []}
    if img.filename:
        tiles_dir = create_tile_directory(img)
        for tileset_group in img.layers:
            export_tileset(img, tiles_dir, tileset_group, json_data)
    with open(os.path.join(tiles_dir, 'tilesets.json'), 'w') as json_file:
        json_file.write(json.dumps(json_data, indent=2))

register(
   proc_name=("tileset_exporter"),
   label=("Export Tilesets"),
   blurb=("Export all layers as a tileset + JSON data"),
   help=("Help?"),
   author=("David Corticchiato"), 
   copyright=("www.twoseasgames.com"), 
   date=("2013"),
   menu=("<Image>/Tilesets"), 
   imagetypes=("*"),
   params=[
      (PF_IMAGE, 'img', 'Select an image', None)
   ],
   results=[],
   function=(export_tilesets)
)

main()


