/**
 * 로거 유틸리티
 */

import { config } from "../config";

type LogLevel = "info" | "warn" | "error" | "debug";

class Logger {
  private log(level: LogLevel, message: string, meta?: Record<string, unknown>): void {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      ...meta,
    };

    if (config.isDevelopment) {
      // 개발 환경: 콘솔에 포맷팅된 로그 출력
      console[level === "error" ? "error" : "log"](
        `[${timestamp}] ${level.toUpperCase()}: ${message}`,
        meta ? JSON.stringify(meta, null, 2) : ""
      );
    } else {
      // 프로덕션 환경: JSON 형태로 출력
      console.log(JSON.stringify(logEntry));
    }
  }

  info(message: string, meta?: Record<string, unknown>): void {
    this.log("info", message, meta);
  }

  warn(message: string, meta?: Record<string, unknown>): void {
    this.log("warn", message, meta);
  }

  error(message: string, error?: Error | unknown, meta?: Record<string, unknown>): void {
    const errorMeta = error instanceof Error
      ? { error: error.message, stack: error.stack, ...meta }
      : { error, ...meta };
    this.log("error", message, errorMeta);
  }

  debug(message: string, meta?: Record<string, unknown>): void {
    if (config.isDevelopment) {
      this.log("debug", message, meta);
    }
  }
}

export const logger = new Logger();
