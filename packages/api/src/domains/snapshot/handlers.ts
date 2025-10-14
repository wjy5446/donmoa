/**
 * Snapshot HTTP Handlers
 * Presentation Layer
 */

import { Request, Response, NextFunction } from "express";
import { AuthenticatedRequest } from "../../types/express";
import { SnapshotService } from "./service";
import { createUserClient } from "../../utils/db";
import { ErrorCode } from "@donmoa/shared";
import { ApiError } from "../../middleware/error";
import { SnapshotCommitInput, SnapshotListQuery } from "./validator";

/**
 * POST /v1/snapshots/commit
 * 스냅샷 커밋
 */
export async function commitSnapshotHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const input = req.body as SnapshotCommitInput;

    const db = createUserClient(authReq.accessToken);
    const service = new SnapshotService(db);

    const result = await service.commitSnapshot(authReq.user.id, input);

    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * POST /v1/snapshots/upload
 * 파일 업로드 후 스냅샷 커밋
 */
export async function uploadSnapshotHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;

    if (!req.file) {
      throw new ApiError(ErrorCode.VALIDATION_ERROR, "No file uploaded");
    }

    const { snapshot_date, notes } = req.body;

    if (!snapshot_date) {
      throw new ApiError(ErrorCode.VALIDATION_ERROR, "snapshot_date is required");
    }

    // TODO: 파일 파싱 로직 구현
    // 현재는 에러 반환
    throw new ApiError(
      ErrorCode.UNPROCESSABLE,
      "File upload parsing not yet implemented. Use /commit endpoint directly."
    );

    // const db = createUserClient(authReq.accessToken);
    // const service = new SnapshotService(db);
    // const result = await service.commitSnapshot(authReq.user.id, parsedData);
    // res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/snapshots
 * 스냅샷 목록 조회
 */
export async function listSnapshotsHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const query = req.query as unknown as SnapshotListQuery;

    const db = createUserClient(authReq.accessToken);
    const service = new SnapshotService(db);

    const result = await service.listSnapshots(authReq.user.id, query);

    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}

/**
 * GET /v1/snapshots/:id
 * 스냅샷 상세 조회
 */
export async function getSnapshotHandler(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authReq = req as AuthenticatedRequest;
    const snapshotId = parseInt(req.params.id, 10);

    if (isNaN(snapshotId)) {
      throw new ApiError(ErrorCode.VALIDATION_ERROR, "Invalid snapshot ID");
    }

    const db = createUserClient(authReq.accessToken);
    const service = new SnapshotService(db);

    const result = await service.getSnapshotById(snapshotId, authReq.user.id);

    if (!result) {
      throw new ApiError(ErrorCode.NOT_FOUND, "Snapshot not found");
    }

    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
}
