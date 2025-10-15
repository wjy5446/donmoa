/**
 * API Routes
 */

import { Router } from "express";
import snapshotRouter from "./snapshot";
import portfolioRouter from "./portfolio";
import analyticsRouter from "./analytics";
import rebalanceRouter from "./rebalance";
import marketRouter from "./market";
import userPrefsRouter from "./user-prefs";

const router = Router();

// Health check
router.get("/health", (req, res) => {
  res.status(200).json({
    status: "ok",
    timestamp: new Date().toISOString(),
    version: "1.0.0",
  });
});

// API v1 routes

// Snapshot Domain
router.use("/v1/snapshots", snapshotRouter);

// Portfolio Domain
router.use("/v1", portfolioRouter); // /accounts, /transactions, /cash, /positions, /dividends

// Analytics Domain
router.use("/v1", analyticsRouter); // /dashboard/*, /cashflow/*, /dividends

// Rebalancing Domain
router.use("/v1/rebalance", rebalanceRouter);

// Market Data Domain
router.use("/v1", marketRouter); // /instruments, /prices/*, /fx/*

// User Preferences Domain
router.use("/v1", userPrefsRouter); // /categories, /favorites, /dashboard/prefs

export default router;
