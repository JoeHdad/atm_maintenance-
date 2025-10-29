You are an AI Engineer working on Feature 6.2: Mobile Responsiveness for a web system.

Your mission:
Optimize the frontend for mobile responsiveness and implement key mobile features.  
After finishing, perform a FULL end-to-end test to ensure every change works properly across all devices, viewports, and functionalities.

---

### 📋 Task Requirements:

#### 🔹 Why:
The current system is not fully optimized for mobile devices.  
We need a **mobile-first** layout and **mobile-friendly UX** that adapts to all screen sizes.

---

### ⚙️ Deliverables:

#### 1. Responsive Design
- Implement a **mobile-first** design approach.  
- Ensure layouts automatically adapt to screen widths (320px – 1024px).  
- Add **touch-friendly buttons** and adequate spacing for accessibility.  
- Apply **media queries** and **responsive CSS utilities** (e.g., Tailwind breakpoints).  
- Enable **swipe gestures** for horizontal navigation or item actions (where logical).  
- Fix any existing UI overflow or horizontal scroll issues.

#### 2. Mobile-Specific Features
- **Camera integration for photo upload:** allow users to capture or upload images via their mobile device.
- **Offline mode (PWA):**
  - Implement caching for static assets and key data.
  - Sync offline actions when the user reconnects.
  - Use Service Workers and PWA manifest for offline capabilities.
- Exclude: Push Notifications, GPS location capture.

---

### 🧠 Technical Guidelines:
- Use Tailwind CSS responsive utilities (sm, md, lg, xl).
- Ensure consistent spacing and typography scaling between breakpoints.
- Use modern React techniques:
  - Hooks for detecting network status (online/offline).
  - Conditional rendering for mobile components.
- Optimize image rendering and layout shifts (CLS).
- Implement viewport meta tag for mobile scaling.
- Ensure scroll and gesture behavior feels native on mobile browsers.

---

### ✅ Acceptance Criteria:
1. All pages render correctly and responsively on:
   - Mobile: 320px–480px  
   - Tablet: 768px  
   - Desktop: 1024px+  
2. No horizontal scrolling or layout overflow.
3. Touch interactions (taps, swipes) work correctly.
4. Camera upload works flawlessly on both Android and iOS browsers.
5. Offline mode allows viewing cached pages and syncs actions once reconnected.
6. Lighthouse mobile score ≥ 90.
7. Smooth performance on Chrome, Safari, and Firefox mobile.

---

### 🧪 Testing Instructions:
After completing implementation, perform a **comprehensive validation**:
- Run mobile view tests in Chrome DevTools and BrowserStack.
- Test all pages, routes, and forms on Android and iOS.
- Simulate offline mode and verify data persistence.
- Check all UI elements for responsiveness and accessibility.
- Verify no console errors or visual bugs across breakpoints.

If any issue appears during testing, fix it immediately before marking the feature as complete.

---


Execute step-by-step.  
Never skip validation.  
At the end, provide a full test summary confirming every deliverable and test case passed successfully.
