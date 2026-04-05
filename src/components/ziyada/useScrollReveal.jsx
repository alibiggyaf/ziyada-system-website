import { useEffect, useRef, useState } from "react";

/**
 * Returns a ref and a boolean `visible`.
 * When the element enters the viewport, visible becomes true (once).
 */
export function useScrollReveal(threshold = 0.15) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          obs.disconnect();
        }
      },
      { threshold }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);

  return [ref, visible];
}

/**
 * Attach to a container — returns an array of { ref, visible } for N children.
 * Each child has a staggered delay.
 */
export function useScrollRevealList(count, threshold = 0.1) {
  const refs = [];
  const [visibles, setVisibles] = useState(new Array(count).fill(false));

  for (let i = 0; i < count; i++) {
    refs.push(useRef(null)); // eslint-disable-line react-hooks/rules-of-hooks
  }

  useEffect(() => {
    const observers = refs.map((ref, i) => {
      if (!ref.current) return null;
      const obs = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            setVisibles(prev => {
              const next = [...prev];
              next[i] = true;
              return next;
            });
            obs.disconnect();
          }
        },
        { threshold }
      );
      obs.observe(ref.current);
      return obs;
    });
    return () => observers.forEach(o => o?.disconnect());
  }, []);

  return refs.map((ref, i) => ({ ref, visible: visibles[i] }));
}