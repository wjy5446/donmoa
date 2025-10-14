/**
 * Money 타입 - 정수화된 금액 표현
 *
 * amount_minor는 통화별 스케일이 적용된 정수값입니다:
 * - KRW: 1 (₩1,000 = 1000)
 * - USD: 100 ($10.50 = 1050)
 * - JPY: 1 (¥1,000 = 1000)
 */
export interface Money {
  amount_minor: bigint;
  currency: string;
}

/**
 * 통화별 스케일 정의
 */
export const CURRENCY_SCALES: Record<string, number> = {
  KRW: 1, // 원화는 소수점 없음
  USD: 100, // 달러는 센트 단위
  EUR: 100,
  GBP: 100,
  JPY: 1, // 엔화는 소수점 없음
  CNY: 100,
};

/**
 * 실수를 정수화된 금액으로 변환
 */
export function toMoneyMinor(amount: number, currency: string): bigint {
  const scale = CURRENCY_SCALES[currency] || 100;
  return BigInt(Math.round(amount * scale));
}

/**
 * 정수화된 금액을 실수로 변환
 */
export function fromMoneyMinor(amountMinor: bigint, currency: string): number {
  const scale = CURRENCY_SCALES[currency] || 100;
  return Number(amountMinor) / scale;
}

/**
 * Money 객체 생성 헬퍼
 */
export function createMoney(amount: number, currency: string): Money {
  return {
    amount_minor: toMoneyMinor(amount, currency),
    currency,
  };
}
