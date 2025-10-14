# @donmoa/ui

공통 UI 컴포넌트 라이브러리

## 개요

React 기반의 재사용 가능한 UI 컴포넌트를 제공합니다.
현재는 Web 앱에서 직접 컴포넌트를 정의하고 있으며, 향후 이 패키지로 이동할 예정입니다.

## TODO

- [ ] shadcn/ui 컴포넌트를 이 패키지로 이동
- [ ] 차트 컴포넌트 (recharts 래퍼)
- [ ] 테이블 컴포넌트 (TanStack Table 래퍼)
- [ ] 폼 컴포넌트 (React Hook Form 통합)
- [ ] 파일 업로드 컴포넌트
- [ ] 대시보드 카드 컴포넌트

## 사용법

```tsx
import { Button, Card } from '@donmoa/ui'

function MyComponent() {
  return (
    <Card>
      <Button>Click me</Button>
    </Card>
  )
}
```

