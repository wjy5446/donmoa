/**
 * API Server Entry Point
 */

import { createApp } from "./app";
import { config, validateConfig } from "./config";
import { logger } from "./utils/logger";

async function main() {
  try {
    // 환경 변수 검증
    validateConfig();

    // Express 앱 생성
    const app = createApp();

    // 서버 시작
    const server = app.listen(config.port, () => {
      logger.info(`Donmoa API Server started`, {
        port: config.port,
        env: config.nodeEnv,
        cors: config.cors.origin,
      });
    });

    // Graceful shutdown
    const shutdown = async () => {
      logger.info("Shutting down server...");
      server.close(() => {
        logger.info("Server closed");
        process.exit(0);
      });

      // 강제 종료 (10초 후)
      setTimeout(() => {
        logger.error("Forced shutdown");
        process.exit(1);
      }, 10000);
    };

    process.on("SIGTERM", shutdown);
    process.on("SIGINT", shutdown);

  } catch (error) {
    logger.error("Failed to start server", error);
    process.exit(1);
  }
}

main();
