/**
 * Snapshot Routes
 */

import { Router } from "express";
import multer from "multer";
import { authMiddleware } from "../middleware/auth";
import { validateBody, validateQuery } from "../middleware/validation";
import { idempotencyMiddleware } from "../middleware/idempotency";
import {
  commitSnapshotHandler,
  uploadSnapshotHandler,
  listSnapshotsHandler,
  getSnapshotHandler,
} from "../domains/snapshot/handlers";
import {
  snapshotCommitSchema,
  snapshotListQuerySchema,
} from "../domains/snapshot/validator";

const router = Router();

// Multer 설정 (메모리 저장)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB
  },
});

/**
 * POST /v1/snapshots/commit
 * 스냅샷 커밋 (JSON 데이터)
 */
router.post(
  "/commit",
  authMiddleware,
  idempotencyMiddleware,
  validateBody(snapshotCommitSchema),
  commitSnapshotHandler
);

/**
 * POST /v1/snapshots/upload
 * 파일 업로드 후 스냅샷 커밋
 */
router.post(
  "/upload",
  authMiddleware,
  upload.single("file"),
  uploadSnapshotHandler
);

/**
 * GET /v1/snapshots
 * 스냅샷 목록 조회
 */
router.get(
  "/",
  authMiddleware,
  validateQuery(snapshotListQuerySchema),
  listSnapshotsHandler
);

/**
 * GET /v1/snapshots/:id
 * 스냅샷 상세 조회
 */
router.get(
  "/:id",
  authMiddleware,
  getSnapshotHandler
);

export default router;
