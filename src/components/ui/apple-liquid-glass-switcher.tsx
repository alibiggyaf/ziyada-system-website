"use client";

import React, { useState, useEffect } from "react";

type Theme = "light" | "dark" | "dim";

interface ThemeSwitcherProps {
  defaultValue?: Theme;
  value?: Theme;
  onValueChange?: (theme: Theme) => void;
}

const themeOptions: { value: Theme; cOption: string; icon: React.ReactNode }[] = [
  {
    value: "light",
    cOption: "1",
    icon: <span className="switcher__emoji">L</span>,
  },
  {
    value: "dark",
    cOption: "2",
    icon: <span className="switcher__emoji">D</span>,
  },
  {
    value: "dim",
    cOption: "3",
    icon: <span className="switcher__emoji">M</span>,
  },
];

export function ThemeSwitcher({
  defaultValue = "light",
  value,
  onValueChange,
}: ThemeSwitcherProps) {
  const [internalValue, setInternalValue] = useState(defaultValue);
  const activeValue = value ?? internalValue;

  useEffect(() => {
    if (value !== undefined) {
      setInternalValue(value);
    }
  }, [value]);

  const handleChange = (newValue: Theme) => {
    if (onValueChange) {
      onValueChange(newValue);
    } else {
      setInternalValue(newValue);
    }
  };

  return (
    <fieldset
      className="switcher"
      data-previous={themeOptions.find((o) => o.value === activeValue)?.cOption}
    >
      <legend className="switcher__legend">Choose theme</legend>

      {themeOptions.map((option) => (
        <label key={option.value} className="switcher__option">
          <input
            className="switcher__input"
            type="radio"
            name="theme"
            value={option.value}
            data-c-option={option.cOption}
            checked={activeValue === option.value}
            onChange={() => handleChange(option.value)}
          />
          {option.icon}
        </label>
      ))}
    </fieldset>
  );
}
