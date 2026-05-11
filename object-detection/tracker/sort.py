"""
SORT: Simple Online and Realtime Tracking
==========================================
A minimal implementation of the SORT tracking algorithm.
Paper: https://arxiv.org/abs/1602.00763
"""

import numpy as np
from scipy.optimize import linear_sum_assignment
from filterpy.kalman import KalmanFilter


def iou_batch(bb_test, bb_gt):
    """Compute IOU between all pairs of boxes in bb_test and bb_gt."""
    bb_gt   = np.expand_dims(bb_gt,   0)
    bb_test = np.expand_dims(bb_test, 1)

    xx1 = np.maximum(bb_test[..., 0], bb_gt[..., 0])
    yy1 = np.maximum(bb_test[..., 1], bb_gt[..., 1])
    xx2 = np.minimum(bb_test[..., 2], bb_gt[..., 2])
    yy2 = np.minimum(bb_test[..., 3], bb_gt[..., 3])

    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)

    wh      = w * h
    area_t  = (bb_test[..., 2] - bb_test[..., 0]) * (bb_test[..., 3] - bb_test[..., 1])
    area_g  = (bb_gt[...,   2] - bb_gt[...,   0]) * (bb_gt[...,   3] - bb_gt[...,   1])
    o       = wh / (area_t + area_g - wh)
    return o


def convert_bbox_to_z(bbox):
    """Convert [x1,y1,x2,y2] to [cx, cy, area, aspect_ratio]."""
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = bbox[0] + w / 2.
    y = bbox[1] + h / 2.
    s = w * h
    r = w / float(h)
    return np.array([x, y, s, r]).reshape((4, 1))


def convert_x_to_bbox(x, score=None):
    """Convert [cx, cy, area, aspect_ratio] back to [x1,y1,x2,y2]."""
    w = np.sqrt(x[2] * x[3])
    h = x[2] / w
    if score is None:
        return np.array([
            x[0] - w / 2., x[1] - h / 2.,
            x[0] + w / 2., x[1] + h / 2.
        ]).reshape((1, 4))
    return np.array([
        x[0] - w / 2., x[1] - h / 2.,
        x[0] + w / 2., x[1] + h / 2.,
        score
    ]).reshape((1, 5))


class KalmanBoxTracker:
    """Represents a tracked object using a Kalman Filter."""

    count = 0

    def __init__(self, bbox):
        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        self.kf.F = np.array([
            [1,0,0,0,1,0,0],
            [0,1,0,0,0,1,0],
            [0,0,1,0,0,0,1],
            [0,0,0,1,0,0,0],
            [0,0,0,0,1,0,0],
            [0,0,0,0,0,1,0],
            [0,0,0,0,0,0,1]
        ], dtype=float)

        self.kf.H = np.array([
            [1,0,0,0,0,0,0],
            [0,1,0,0,0,0,0],
            [0,0,1,0,0,0,0],
            [0,0,0,1,0,0,0]
        ], dtype=float)

        self.kf.R[2:, 2:] *= 10.
        self.kf.P[4:, 4:] *= 1000.
        self.kf.P         *= 10.
        self.kf.Q[-1, -1] *= 0.01
        self.kf.Q[4:, 4:] *= 0.01
        self.kf.x[:4]      = convert_bbox_to_z(bbox)

        KalmanBoxTracker.count += 1
        self.id           = KalmanBoxTracker.count
        self.history      = []
        self.hits         = 0
        self.hit_streak   = 0
        self.age          = 0
        self.time_since_update = 0

    def update(self, bbox):
        self.time_since_update = 0
        self.history           = []
        self.hits             += 1
        self.hit_streak       += 1
        self.kf.update(convert_bbox_to_z(bbox))

    def predict(self):
        if (self.kf.x[6] + self.kf.x[2]) <= 0:
            self.kf.x[6] *= 0.0
        self.kf.predict()
        self.age += 1
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1
        self.history.append(convert_x_to_bbox(self.kf.x))
        return self.history[-1]

    def get_state(self):
        return convert_x_to_bbox(self.kf.x)


def associate_detections_to_trackers(detections, trackers, iou_threshold=0.3):
    """Match detections to existing trackers using IOU."""
    if len(trackers) == 0:
        return (
            np.empty((0, 2), dtype=int),
            np.arange(len(detections)),
            np.empty((0, 5), dtype=int)
        )

    iou_matrix = iou_batch(detections, trackers)

    if min(iou_matrix.shape) > 0:
        a = (iou_matrix > iou_threshold).astype(np.int32)
        if a.sum(1).max() == 1 and a.sum(0).max() == 1:
            matched_indices = np.stack(np.where(a), axis=1)
        else:
            row_ind, col_ind = linear_sum_assignment(-iou_matrix)
            matched_indices  = np.stack([row_ind, col_ind], axis=1)
    else:
        matched_indices = np.empty((0, 2), dtype=int)

    unmatched_detections = [
        d for d in range(len(detections))
        if d not in matched_indices[:, 0]
    ]
    unmatched_trackers = [
        t for t in range(len(trackers))
        if t not in matched_indices[:, 1]
    ]

    matches = [
        m for m in matched_indices
        if iou_matrix[m[0], m[1]] >= iou_threshold
    ]
    unmatched_detections += [
        m[0] for m in matched_indices
        if iou_matrix[m[0], m[1]] < iou_threshold
    ]

    if len(matches) == 0:
        matches = np.empty((0, 2), dtype=int)
    else:
        matches = np.array(matches)

    return matches, np.array(unmatched_detections), np.array(unmatched_trackers)


class Sort:
    """SORT multi-object tracker."""

    def __init__(self, max_age=30, min_hits=2, iou_threshold=0.3):
        self.max_age       = max_age
        self.min_hits      = min_hits
        self.iou_threshold = iou_threshold
        self.trackers      = []
        self.frame_count   = 0
        KalmanBoxTracker.count = 0

    def update(self, dets=np.empty((0, 5))):
        """
        dets: np.array of shape (N, 5) → [x1, y1, x2, y2, score]
        Returns: np.array of shape (M, 5) → [x1, y1, x2, y2, track_id]
        """
        self.frame_count += 1

        # Predict new positions for all trackers
        trks  = np.zeros((len(self.trackers), 5))
        to_del = []
        for i, trk in enumerate(trks):
            pos = self.trackers[i].predict()[0]
            trk[:] = [pos[0], pos[1], pos[2], pos[3], 0]
            if np.any(np.isnan(pos)):
                to_del.append(i)

        trks = np.ma.compress_rows(np.ma.masked_invalid(trks))
        for i in reversed(to_del):
            self.trackers.pop(i)

        matched, unmatched_dets, unmatched_trks = associate_detections_to_trackers(
            dets[:, :4], trks[:, :4], self.iou_threshold
        )

        # Update matched trackers
        for m in matched:
            self.trackers[m[1]].update(dets[m[0], :])

        # Create new trackers for unmatched detections
        for i in unmatched_dets:
            self.trackers.append(KalmanBoxTracker(dets[i, :]))

        # Build result
        ret = []
        for trk in reversed(self.trackers):
            d = trk.get_state()[0]
            if (trk.time_since_update < 1) and (
                trk.hit_streak >= self.min_hits or self.frame_count <= self.min_hits
            ):
                ret.append(np.concatenate((d, [trk.id])).reshape(1, -1))

        # Remove dead trackers
        self.trackers = [
            t for t in self.trackers
            if t.time_since_update <= self.max_age
        ]

        if len(ret) > 0:
            return np.concatenate(ret)
        return np.empty((0, 5))
