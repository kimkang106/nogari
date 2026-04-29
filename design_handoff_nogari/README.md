# Handoff: nogari — Fish-Shaped Gallery

## Overview
**nogari**는 물고기 모양의 인터랙티브 갤러리 웹페이지입니다.  
물고기 몸통의 비늘 각각이 클릭 가능한 썸네일 이미지이며, 클릭하면 오른쪽에서 슬라이드되는 상세 패널이 열립니다. CMS(Notion API 또는 Airtable)에서 콘텐츠를 불러와 수시로 업데이트할 수 있는 구조입니다.

## About the Design Files
이 폴더의 `index.html`은 **HTML로 제작된 디자인 레퍼런스(프로토타입)**입니다.  
실제 프로덕션 코드로 그대로 사용하는 것이 아니라, **이 디자인을 기반으로 실제 프레임워크(Next.js, React, Vue 등) 환경에서 재구현**하는 것이 목표입니다. 기존 코드베이스가 없다면 **React + Next.js** 사용을 권장합니다.

## Fidelity
**High-fidelity (hifi)** — 최종 색상, 타이포그래피, 간격, 인터랙션이 모두 포함된 픽셀 퀄리티 목업입니다. 디자인을 최대한 그대로 재현해 주세요.

---

## Screen: 메인 페이지 (Fish Gallery)

### 레이아웃
- `100vw × 100vh` 전체 화면, `overflow: hidden`
- 물고기 SVG가 화면 중앙에 수직/수평 정렬 (`display: flex; align-items: center; justify-content: center`)
- 물고기 너비: `min(96vw, 1200px)`, 비율 유지 (`height: auto`)
- 물고기는 위아래로 천천히 둥실거리는 float 애니메이션 적용

### 배경
| 요소 | 설명 |
|---|---|
| 배경색 | `#0a2240` (밝은 심해 파란색) |
| 빛 기둥 | SVG로 구현된 세로 반투명 폴리곤 6개, `opacity: 0.14`, 위에서 아래로 연한 파란색 그라디언트 |
| 버블 | 22개 원형 div, 아래에서 위로 `floatBubble` 키프레임 애니메이션, 크기 4~22px, `border: 1px solid oklch(0.72 0.12 200 / 0.25)` |
| 해초 | SVG 베지어 곡선 4개, `sway` 키프레임으로 좌우 흔들림, 화면 하단 좌우에 배치 |

### 물고기 SVG (ViewBox: `0 0 900 500`)

#### 몸통 (Body)
```svg
<path d="M 738,250
  C 732,208 716,174 692,152
  C 666,128 634,116 596,110
  C 554,104 506,103 456,105
  C 406,107 358,113 312,124
  C 268,135 230,150 200,170
  C 172,190 156,216 150,245
  C 144,274 154,302 174,324
  C 196,348 228,364 268,376
  C 310,388 358,394 410,393
  C 462,392 514,388 562,380
  C 606,372 646,358 678,338
  C 710,318 730,292 738,262
  C 740,258 740,254 738,250 Z" />
```
- Fill: `linearGradient` — `oklch(0.19 0.15 218)` → `oklch(0.12 0.09 210)` (좌→우)
- Stroke: `oklch(0.50 0.22 205 / 0.38)`, strokeWidth: `1.8`

#### 꼬리 지느러미 (Tail)
```
M 148,250 L 48,162 L 96,250 L 48,338 Z
```
- Fill: `finGrad` (동일 그라디언트, 대각선)
- Stroke: `oklch(0.48 0.2 210 / 0.5)`, strokeWidth: `1.5`

#### 등지느러미 (Dorsal Fin)
```
M 368,114 C 392,72 445,54 508,70 C 546,82 568,102 570,114 Z
```

#### 가슴지느러미 (Pectoral Fin)
```
M 608,222 C 588,254 572,284 596,304 C 624,290 648,268 644,246 Z
```
- Fill: `oklch(0.20 0.15 218)`

#### 측선 (Lateral Line)
- Dotted dash line: `strokeDasharray: "3 6"`, `stroke: oklch(0.55 0.16 200 / 0.18)`

---

### 눈 (Eye)
- 위치: `cx=700, cy=210`
- 흰자(Sclera): `r=30`, fill: `oklch(0.92 0.03 210)`
- 홍채(Iris): `r=22`, fill: `oklch(0.40 0.24 195)`
- 홍채 내부링: `r=16`, stroke: `oklch(0.60 0.26 185)`, strokeWidth: `1.5`
- 동공(Pupil): `r=11`, fill: `#040c18`
- 하이라이트: `r=4.5`, fill: `white`, opacity: `0.85` — 동공 기준 (-4, -4) 위치
- 아웃라인: stroke `oklch(0.42 0.18 215)`, strokeWidth: `1.8`

#### 눈 애니메이션
동공이 **렘니스케이트(∞ 모양)** 패턴으로 천천히 움직입니다:
```javascript
// requestAnimationFrame 루프
t += 0.006; // 매우 느린 속도
pupilX = EYE_CX + Math.sin(t) * 6;
pupilY = EYE_CY + Math.sin(t * 2) * 3;
```

---

### 비늘 (Scales) — 55개

#### 배치 알고리즘
- **Hexagonal packing**: 짝수 행은 그대로, 홀수 행은 `COL_STEP / 2` 만큼 오프셋
- `SCALE_R = 21px`
- `COL_STEP = SCALE_R * 2 * 0.92 ≈ 38.6px`
- `ROW_STEP = SCALE_R * √3 * 0.90 ≈ 32.7px`
- 시작: `x=162, y=120`
- 물고기 body polygon 내부에 있는 점만 채택 (`point-in-polygon` 테스트)
- 눈 중심에서 `EYE_R + 20 = 50px` 이내 점은 제외

#### 각 비늘 렌더링
```svg
<!-- clipPath로 원형 마스크 -->
<clipPath id="sc-{i}">
  <circle cx={x} cy={y} r={SCALE_R - 1} />
</clipPath>

<!-- 배경 원 -->
<circle cx={x} cy={y} r={SCALE_R} fill="oklch(0.12 0.1 215)" />

<!-- 썸네일 이미지 (CMS에서 로드) -->
<image href={item.thumb} ... clipPath="url(#sc-{i})" />

<!-- 테두리 -->
<circle cx={x} cy={y} r={SCALE_R - 0.5}
  fill="none" stroke="oklch(0.55 0.18 195 / 0.55)" strokeWidth="1.5" />

<!-- 비늘 하이라이트 arc -->
<path d="M {x-r*0.8} {y+r*0.1} A ... {x+r*0.8} {y+r*0.1}"
  stroke="oklch(0.75 0.15 200 / 0.12)" />
```

#### 호버 상태
- `stroke` → `oklch(0.85 0.28 185)`, strokeWidth: `2`
- `image` → `filter: brightness(1.35) saturate(1.2)`
- `cursor: pointer`

---

## Screen: 상세 오버레이 (Slide Overlay)

비늘 클릭 시 오른쪽에서 슬라이드인.

### 레이아웃
- `position: fixed; right: 0; top: 0; height: 100%; width: min(420px, 100vw)`
- Transform: `translateX(100%)` → `translateX(0)` (0.45s, `cubic-bezier(0.4,0,0.2,1)`)
- Background: `linear-gradient(165deg, #040f24, #020a1c)`
- Border-left: `1px solid oklch(0.55 0.15 200 / 0.25)`
- z-index: `100`

### 구성 요소
| 요소 | 스펙 |
|---|---|
| 이미지 | 너비 100%, aspect-ratio 4:3, `object-fit: cover` |
| 닫기 버튼 | 우상단 `32×32px` 원형, `position: absolute` |
| 메타 텍스트 | `11px`, `letter-spacing: 0.12em`, `text-transform: uppercase`, color: `oklch(0.62 0.15 195)` |
| 제목 | `22px`, `font-weight: 600`, color: `#e8f4fb` |
| 설명 | `14px`, `line-height: 1.7`, color: `oklch(0.68 0.06 210)` |
| 원문 링크 | 테두리 버튼, `border: 1px solid oklch(0.55 0.18 195 / 0.4)`, border-radius: `4px` |

### 백드롭
- 클릭 시 배경 어둡게: `rgba(1, 5, 18, 0.72)`, transition `0.4s`
- 백드롭 클릭 → 오버레이 닫기
- ESC 키 → 닫기

---

## 애니메이션 정리

| 이름 | 대상 | 설명 |
|---|---|---|
| `fishFloat` | `.fish-wrap` | `translateY 0 → -10px → 0`, 5s, ease-in-out, infinite |
| `floatBubble` | `.bubble` | 아래→위 이동, 7~19s, linear, 랜덤 delay |
| `sway` | `.seaweed-group` | `rotate(-6deg) ↔ rotate(6deg)`, 3.5~4.8s, ease-in-out |
| Eye pupil | `<circle>` (pupil) | rAF 루프, 렘니스케이트, t+=0.006 |
| Scale hover | CSS | filter + stroke transition 0.2s |
| Overlay | CSS transform | translateX 0.45s cubic-bezier |

---

## CMS 연결 구조

현재 프로토타입의 `DEMO_ITEMS` 배열을 실제 API 호출로 교체합니다.

### 추천 플랫폼: Notion API (코딩 없이 관리 가능)

```javascript
// Notion API 연결 예시
async function fetchItems() {
  const response = await fetch('https://api.notion.com/v1/databases/{DATABASE_ID}/query', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.NOTION_TOKEN}`,
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json',
    },
  });
  const data = await response.json();
  return data.results.map(page => ({
    id: page.id,
    title: page.properties.Title.title[0]?.plain_text,
    image: page.properties.Image.files[0]?.file?.url,
    thumb: page.properties.Thumbnail.files[0]?.file?.url,
    description: page.properties.Description.rich_text[0]?.plain_text,
    date: page.properties.Date.date?.start,
    url: page.properties.URL.url,
  }));
}
```

### 대안: Airtable API
```javascript
async function fetchItemsAirtable() {
  const response = await fetch(
    `https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}`,
    { headers: { Authorization: `Bearer ${process.env.AIRTABLE_TOKEN}` } }
  );
  const data = await response.json();
  return data.records.map(r => ({
    id: r.id,
    title: r.fields.Title,
    image: r.fields.Image?.[0]?.url,
    thumb: r.fields.Thumbnail?.[0]?.url,
    description: r.fields.Description,
    date: r.fields.Date,
    url: r.fields.URL,
  }));
}
```

### Notion 데이터베이스 컬럼 구조
| 컬럼명 | 타입 | 설명 |
|---|---|---|
| Title | Title | 작품 제목 |
| Image | Files & media | 상세 이미지 (800×600 권장) |
| Thumbnail | Files & media | 비늘 썸네일 (120×120 권장) |
| Description | Text | 작품 설명 |
| Date | Date | 게시 날짜 |
| URL | URL | 원문 링크 (선택) |

---

## 디자인 토큰

### 색상
| 이름 | 값 | 용도 |
|---|---|---|
| Background | `#0a2240` | 배경 |
| Fish Body Dark | `oklch(0.19 0.15 218)` | 몸통 그라디언트 시작 |
| Fish Body Light | `oklch(0.12 0.09 210)` | 몸통 그라디언트 끝 |
| Glow Cyan | `oklch(0.55 0.22 200)` | drop-shadow glow |
| Scale Border | `oklch(0.55 0.18 195 / 0.55)` | 비늘 테두리 |
| Scale Hover | `oklch(0.85 0.28 185)` | 호버 시 테두리 |
| Eye Iris | `oklch(0.40 0.24 195)` | 홍채 |
| Text Primary | `#e8f4fb` | 오버레이 제목 |
| Text Secondary | `oklch(0.68 0.06 210)` | 오버레이 본문 |
| Text Meta | `oklch(0.62 0.15 195)` | 날짜/ID 등 메타 |

### 타이포그래피
- Font family: `'Helvetica Neue', Helvetica, Arial, sans-serif`
- Site title: `13px`, `letter-spacing: 0.25em`, `text-transform: uppercase`
- Overlay title: `22px / 600 / -0.01em letter-spacing`
- Overlay body: `14px / 1.7 line-height`
- Meta: `11px / 0.12em letter-spacing / uppercase`

### 간격 & 형태
- Overlay padding: `28px`
- Scale radius: `21px`
- Eye radius: `30px`
- Overlay width: `min(420px, 100vw)`
- Border radius (버튼): `4px`
- Overlay transition: `0.45s cubic-bezier(0.4, 0, 0.2, 1)`

---

## 파일 목록
| 파일 | 설명 |
|---|---|
| `index.html` | 전체 프로토타입 (React + Babel inline) |

---

## 구현 권장 사항

1. **Next.js App Router** 사용 권장 (서버 컴포넌트에서 CMS API 호출)
2. SVG는 인라인으로 렌더링 (외부 파일 X) — React 컴포넌트로 분리 가능
3. 비늘 이미지 로딩: `next/image` 또는 lazy loading 적용
4. `point-in-polygon` 계산은 빌드 타임에 미리 계산해 정적 데이터로 저장 권장
5. 오버레이 상태: URL query param (`?item=ID`)으로 관리하면 공유 가능
6. CMS API는 Next.js Route Handler로 감싸서 토큰 노출 방지
