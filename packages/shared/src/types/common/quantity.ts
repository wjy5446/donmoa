/**
 * Quantity 타입 - 정수화된 수량 표현
 *
 * qty_nano = 수량 × 1,000,000,000 (10^9)
 * 소수점 9자리까지 정밀하게 표현 가능
 */

const NANO_SCALE = 1_000_000_000;

/**
 * 실수 수량을 nano 단위 정수로 변환
 */
export function toQtyNano(quantity: number): bigint {
  return BigInt(Math.round(quantity * NANO_SCALE));
}

/**
 * nano 단위 정수를 실수 수량으로 변환
 */
export function fromQtyNano(qtyNano: bigint): number {
  return Number(qtyNano) / NANO_SCALE;
}

/**
 * Price 타입 - 정수화된 단가 표현
 */
export function toPriceNano(price: number): bigint {
  return BigInt(Math.round(price * NANO_SCALE));
}

export function fromPriceNano(priceNano: bigint): number {
  return Number(priceNano) / NANO_SCALE;
}
