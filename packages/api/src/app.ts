/**
 * Express Application
 */

import express, { Application } from "express";
import cors from "cors";
import helmet from "helmet";
import compression from "compression";
import { config } from "./config";
import { logger } from "./utils/logger";
import { errorHandler, notFoundHandler } from "./middleware/error";
import routes from "./routes";

export function createApp(): Application {
  const app = express();

  // Security
  app.use(helmet());
  app.use(cors(config.cors));

  // Compression
  app.use(compression());

  // Body parsing
  app.use(express.json({ limit: "10mb" }));
  app.use(express.urlencoded({ extended: true, limit: "10mb" }));

  // Request logging (simple)
  app.use((req, _res, next) => {
    logger.info(`${req.method} ${req.path}`, {
      query: req.query,
      ip: req.ip,
    });
    next();
  });

  // Routes
  app.use("/", routes);

  // Error handlers
  app.use(notFoundHandler);
  app.use(errorHandler);

  return app;
}
