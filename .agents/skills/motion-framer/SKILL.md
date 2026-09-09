---
name: motion-framer
description: >-
  Master UI/UX Motion Design & Animation Skill for Framer Motion, Tailwind CSS, React, and Modern Web UIs.
  Provides animation presets, micro-interactions, layout transitions, glassmorphic design systems, and enterprise-grade UI aesthetics.
---

# Motion Framer: Professional UI/UX & Motion Engineering System

This skill equips agents and developers with the exact principles, physics curves, component architectures, and visual polish required to build world-class, Apple-grade, and Linear-grade user interfaces using **Framer Motion**, **Tailwind CSS**, and modern web standards.

---

## 1. Core Principles of Premium Motion Design

1. **Physics Over Linear Easing:** Never use `ease-in-out` for interactive elements. Always use spring physics (`type: "spring"`) to mimic real-world inertia, mass, and tension.
2. **Subtlety & Intent:** Animations should communicate state changes, spatial hierarchy, or cause-and-effect. Never animate for the sake of animating.
3. **Respect Performance (GPU Only):** Only animate composited properties: `transform` (`x`, `y`, `scale`, `rotate`) and `opacity`. Avoid animating `width`, `height`, `top`, or `margin` directly; use `layout` or `scale` instead.
4. **Optimistic & Fast:** Entrance animations should take 150ms–350ms. Any interaction taking longer than 400ms feels sluggish to the user.
5. **Accessibility (Reduced Motion):** Always respect `useReducedMotion()` or CSS `@media (prefers-reduced-motion: reduce)`.

---

## 2. Universal Spring Physics Presets

Use these standardized spring presets across all UI components:

```typescript
export const MOTION_SPRINGS = {
  // Snappy: Best for buttons, toggles, icon clicks, and hover states
  snappy: { type: "spring", stiffness: 400, damping: 30 },

  // Gentle: Best for modals, drawers, and page content entrances
  gentle: { type: "spring", stiffness: 260, damping: 20 },

  // Bouncy: Best for badges, notifications, success checks, and celebratory UI
  bouncy: { type: "spring", stiffness: 300, damping: 10, mass: 0.8 },

  // Smooth: Best for large sheets, slide-overs, and bottom navigation
  smooth: { type: "spring", stiffness: 180, damping: 24 },

  // Micro: Ultra-fast tactile feedback for tabs, cards, and list items
  micro: { type: "spring", stiffness: 500, damping: 35 }
};
```

---

## 3. Standard Orchestration Variants

### Staggered Container & Child Entrance
```typescript
export const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.06,
      delayChildren: 0.1,
    }
  }
};

export const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { type: "spring", stiffness: 300, damping: 24 }
  }
};
```

### Fade & Scale Modal Overlay
```typescript
export const modalOverlayVariants = {
  hidden: { opacity: 0, backdropFilter: "blur(0px)" },
  visible: { 
    opacity: 1, 
    backdropFilter: "blur(8px)",
    transition: { duration: 0.2 } 
  },
  exit: { 
    opacity: 0, 
    backdropFilter: "blur(0px)",
    transition: { duration: 0.15 } 
  }
};

export const modalContentVariants = {
  hidden: { opacity: 0, scale: 0.95, y: 10 },
  visible: { 
    opacity: 1, 
    scale: 1, 
    y: 0,
    transition: { type: "spring", stiffness: 350, damping: 25 } 
  },
  exit: { 
    opacity: 0, 
    scale: 0.96, 
    y: 8,
    transition: { duration: 0.15 } 
  }
};
```

---

## 4. Layout Animations & Shared Elements (`layoutId`)

When elements change position, size, or active tab state, use `layout` and `layoutId` to achieve 60fps morphing animations without manual coordinate math:

### Sliding Active Tab Indicator (Apple / Linear style)
```tsx
import { useState } from "react";
import { motion } from "framer-motion";

const tabs = ["All Leads", "Submitted (Live)", "Ready", "Settings"];

export function SlidingTabs() {
  const [activeTab, setActiveTab] = useState(tabs[0]);

  return (
    <div className="flex items-center gap-1 p-1.5 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200/60 dark:border-slate-700/60">
      {tabs.map((tab) => {
        const isActive = activeTab === tab;
        return (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`relative px-4 py-2 text-xs font-semibold rounded-lg transition-colors z-10 ${
              isActive ? "text-slate-900 dark:text-white" : "text-slate-500 hover:text-slate-800"
            }`}
          >
            {tab}
            {isActive && (
              <motion.div
                layoutId="active-pill"
                className="absolute inset-0 bg-white dark:bg-slate-700 rounded-lg shadow-sm -z-10"
                transition={{ type: "spring", stiffness: 450, damping: 35 }}
              />
            )}
          </button>
        );
      })}
    </div>
  );
}
```

---

## 5. Micro-Interactions & Tactile Gestures

Every interactive element should respond with high-fidelity visual and haptic feedback:

```tsx
// 1. Tactile Button
<motion.button
  whileHover={{ scale: 1.02, y: -1 }}
  whileTap={{ scale: 0.97 }}
  transition={{ type: "spring", stiffness: 400, damping: 25 }}
  className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl shadow-md shadow-indigo-500/20 active:shadow-sm"
>
  Auto-Submit Batch
</motion.button>

// 2. Interactive Card with Ambient Glow
<motion.div
  whileHover={{ y: -4, boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.04)" }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
  className="p-5 bg-white dark:bg-slate-900 border border-slate-200/80 rounded-2xl cursor-pointer"
>
  <h3>Indore Saturation</h3>
</motion.div>
```

---

## 6. Visual Design System: Glassmorphism & Mesh Lighting

Modern enterprise UI requires high aesthetic sophistication:

1. **Frosted Glass Cards:**
   ```html
   class="bg-white/75 dark:bg-slate-900/75 backdrop-blur-xl border border-white/30 dark:border-white/10 shadow-xl shadow-slate-200/50 dark:shadow-none"
   ```

2. **Subtle Mesh Background:**
   ```html
   class="bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-100/50 via-slate-50 to-white dark:from-slate-900 dark:via-slate-950 dark:to-black min-h-screen"
   ```

3. **Status Badges with Pulse:**
   ```tsx
   <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60">
     <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
     Live Sync
   </span>
   ```

---

## 7. Quality Checklist Before Shipping UI

- [ ] Does every modal, tooltip, and toast have an entrance AND an exit animation wrapped in `<AnimatePresence>`?
- [ ] Are active navigation states using `layoutId` for smooth pill transitions?
- [ ] Are list items animated with staggered delay rather than appearing all at once?
- [ ] Are buttons using spring physics for `whileTap` scale reduction?
- [ ] Is mobile touch responsiveness validated (no hover stickiness on touch screens)?
- [ ] Are all animations tested with `prefers-reduced-motion`?
