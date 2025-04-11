import cv2
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from sklearn.cluster import DBSCAN
import random


def detect_hough_lines(skeleton_img, min_line_length=40, max_line_gap=3):
    lines = cv2.HoughLinesP(
        skeleton_img,
        rho=1,
        theta=np.pi / 180,
        threshold=50,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap
    )
    return lines


def line_to_angle_intercept(x1, y1, x2, y2):
    if x2 == x1:
        angle = np.pi / 2
        intercept = x1
    else:
        angle = np.arctan2((y2 - y1), (x2 - x1))
        intercept = y1 - np.tan(angle) * x1
    return angle, intercept


def dual_cluster_lines(lines, image_shape):
    angles = []
    intercepts = []
    coords = []

    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle, intercept = line_to_angle_intercept(x1, y1, x2, y2)
        angles.append([angle])
        intercepts.append(intercept)
        coords.append((x1, y1, x2, y2))

    angles = np.array(angles, dtype=np.float32)
    slope_db = DBSCAN(eps=0.1, min_samples=2).fit(angles)
    slope_labels = slope_db.labels_

    print(f"Slope Clusters Found: {len(set(slope_labels)) - (1 if -1 in slope_labels else 0)}")

    grouped = {}
    slope_intercept_map = []

    for i, slope_label in enumerate(slope_labels):
        if slope_label == -1:
            continue
        grouped.setdefault(slope_label, []).append((intercepts[i], coords[i]))
        slope_intercept_map.append((slope_label, intercepts[i], coords[i]))

    final_clusters = []
    intercept_cluster_map = []

    for slope_label, lines_data in grouped.items():
        intercept_vals = np.array([[i[0] / image_shape[0]] for i in lines_data], dtype=np.float32)  # normalized
        intercept_db = DBSCAN(eps=0.03, min_samples=2).fit(intercept_vals)
        intercept_labels = intercept_db.labels_

        print(f"  Intercept Clusters in Slope Group {slope_label}: {len(set(intercept_labels)) - (1 if -1 in intercept_labels else 0)}")

        for j, label in enumerate(intercept_labels):
            if label == -1:
                continue
            cluster = [lines_data[k][1] for k in range(len(lines_data)) if intercept_labels[k] == label]
            final_clusters.append(cluster)
            for k in range(len(lines_data)):
                if intercept_labels[k] == label:
                    intercept_cluster_map.append((slope_label, label, lines_data[k][1]))

    return final_clusters, slope_intercept_map, intercept_cluster_map


def average_line(line_group):
    xs, ys = [], []
    for x1, y1, x2, y2 in line_group:
        xs.extend([x1, x2])
        ys.extend([y1, y2])
    [vx, vy, x0, y0] = cv2.fitLine(np.array(list(zip(xs, ys)), dtype=np.int32), cv2.DIST_L2, 0, 0.01, 0.01)
    length = 1000
    x1 = int(x0 - vx * length)
    y1 = int(y0 - vy * length)
    x2 = int(x0 + vx * length)
    y2 = int(y0 + vy * length)
    return x1, y1, x2, y2


def deduplicate_lines(lines, angle_thresh=0.05, dist_thresh=10):
    unique_lines = []
    for line in lines:
        x1, y1, x2, y2 = line
        theta = np.arctan2(y2 - y1, x2 - x1)
        bias = y1 - np.tan(theta) * x1
        is_duplicate = False
        for lx1, ly1, lx2, ly2 in unique_lines:
            ltheta = np.arctan2(ly2 - ly1, lx2 - lx1)
            lbias = ly1 - np.tan(ltheta) * lx1
            if abs(theta - ltheta) < angle_thresh and abs(bias - lbias) < dist_thresh:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_lines.append(line)
    return unique_lines


def compute_intersection(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2
    A1, B1 = y2 - y1, x1 - x2
    C1 = A1 * x1 + B1 * y1
    A2, B2 = y4 - y3, x3 - x4
    C2 = A2 * x3 + B2 * y3
    determinant = A1 * B2 - A2 * B1
    if determinant == 0:
        return None
    x = (C1 * B2 - C2 * B1) / determinant
    y = (A1 * C2 - A2 * C1) / determinant
    return int(x), int(y)


def filter_intersections(intersections, image_shape, margin=10):
    h, w = image_shape[:2]
    return [pt for pt in intersections if margin < pt[0] < w - margin and margin < pt[1] < h - margin]


def visualize_hough_and_corners(skeleton_img):
    lines = detect_hough_lines(skeleton_img)
    if lines is None:
        print("No lines detected.")
        return

    final_clusters, slope_intercept_map, intercept_cluster_map = dual_cluster_lines(lines, skeleton_img.shape)

    vis = cv2.cvtColor(skeleton_img, cv2.COLOR_GRAY2BGR)

    # Assign colors per (slope_label, intercept_label)
    color_map = {}
    unique_groups = set((s, i) for s, i, _ in intercept_cluster_map)
    for group in unique_groups:
        color_map[group] = tuple(np.random.randint(0, 255, 3).tolist())

    # Draw all lines grouped by slope+intercept
    for slope_label, intercept_label, (x1, y1, x2, y2) in intercept_cluster_map:
        color = color_map[(slope_label, intercept_label)]
        cv2.line(vis, (x1, y1), (x2, y2), color, 1)

    averaged_lines = [average_line(group) for group in final_clusters]
    deduped_lines = deduplicate_lines(averaged_lines)

    intersections = []
    for line1, line2 in combinations(deduped_lines, 2):
        pt = compute_intersection(line1, line2)
        if pt:
            intersections.append(pt)

    valid_corners = filter_intersections(intersections, skeleton_img.shape)
    for pt in valid_corners:
        cv2.circle(vis, pt, 3, (0, 0, 255), -1)

    plt.figure(figsize=(10, 10))
    plt.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
    plt.title(f"{len(valid_corners)} Corners from Deduplicated Line Intersections")
    plt.axis("off")
    plt.show()

    return valid_corners


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python hough_corner_detector.py path/to/skeleton.png")
    else:
        skeleton = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
        visualize_hough_and_corners(skeleton)
