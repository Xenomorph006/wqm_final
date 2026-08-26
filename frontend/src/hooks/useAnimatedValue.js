import { useEffect, useRef, useState } from "react";

/**
 * Eases a displayed number from its previous value toward `target`.
 * Used so dashboard stats never "pop" straight from 0 to a real number —
 * they climb gradually once the backend starts reporting data.
 */
export function useAnimatedValue(target, duration = 800) {
  const [display, setDisplay] = useState(0);
  const frame = useRef();
  const start = useRef();
  const from = useRef(0);

  useEffect(() => {
    from.current = display;
    start.current = null;

    const step = (ts) => {
      if (!start.current) start.current = ts;
      const progress = Math.min((ts - start.current) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
      setDisplay(from.current + (target - from.current) * eased);
      if (progress < 1) frame.current = requestAnimationFrame(step);
    };

    frame.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target, duration]);

  return display;
}
