import numpy as np
import cv2


def color_threshold(img, R_range=(255, 110), G_range=(255, 110), B_range=(100, 0)):
    R, G, B = img[..., 0], img[..., 1], img[..., 2]
    threshed = np.zeros_like(R)
    selector = (R <= R_range[0]) & (R >= R_range[1]) & (
        G <= G_range[0]) & (G >= G_range[1]) & (B <= B_range[0]) & (B >= B_range[1])
    threshed[selector] = 255

    selector = (img[..., 0] == 0) & (img[..., 1] == 0) & (img[..., 2] == 0)
    threshed[selector] = 0
    return threshed


def rover_coords(binary_img):
    ypos, xpos = binary_img.nonzero()
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2).astype(np.float)
    return x_pixel, y_pixel


def to_polar_coords(x_pixel, y_pixel):
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles


def rotate_pix(xpix, ypix, yaw):
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))

    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    return xpix_rotated, ypix_rotated


def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale):
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    return xpix_translated, ypix_translated


def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    return x_pix_world, y_pix_world


def perspect_transform(img, src, dst):
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))
    return warped


def perception_step(Rover):
    # 1)
    yaw = Rover.yaw
    xpos, ypos = Rover.pos[0], Rover.pos[1]
    world_size = 200
    scale = 10
    image = Rover.img
    dst_size = 5
    bottom_offset = 6
    source = np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
    destination = np.float32([
        [image.shape[1]/2 - dst_size, image.shape[0] - bottom_offset],
        [image.shape[1]/2 + dst_size, image.shape[0] - bottom_offset],
        [image.shape[1]/2 + dst_size, image.shape[0] - 2*dst_size - bottom_offset],
        [image.shape[1]/2 - dst_size, image.shape[0] - 2*dst_size - bottom_offset],
    ])
    # 2)
    warped = perspect_transform(Rover.img, source, destination)
    # 3)
    navigable = color_threshold(
        warped, R_range=(255, 171), G_range=(255, 171), B_range=(255, 171))
    rocks = color_threshold(
        warped, R_range=(255, 120), G_range=(255, 120), B_range=(100, 0))
    obstacles = color_threshold(
        warped, R_range=(120, 0), G_range=(120, 0), B_range=(120, 0))
    # 4)
    Rover.vision_image[:, :, 0] = obstacles
    Rover.vision_image[:, :, 1] = rocks
    Rover.vision_image[:, :, 2] = navigable
    # 5)
    xpix, ypix = rover_coords(navigable)
    rock_x, rock_y = rover_coords(rocks)
    obstacle_x, obstacle_y = rover_coords(obstacles)
    # 6)
    navigable_x_world, navigable_y_world = pix_to_world(
        xpix, ypix, xpos, ypos, yaw, world_size, scale)
    rock_x_world, rock_y_world = pix_to_world(
        rock_x, rock_y, xpos, ypos, yaw, world_size, scale)
    obstacle_x_world, obstacle_y_world = pix_to_world(
        obstacle_x, obstacle_y, xpos, ypos, yaw, world_size, scale)
    # 7)
    Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
    Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
    Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    # 8)
    rover_centric_pixel_distances, rover_centric_angles = to_polar_coords(
        xpix, ypix)
    Rover.nav_dists = rover_centric_pixel_distances
    Rover.nav_angles = rover_centric_angles

    return Rover
