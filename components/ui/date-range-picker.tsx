// frontend/components/ui/date-range-picker.tsx
"use client";

import * as React from "react";
import { format, subMonths } from "date-fns";
import { Calendar as CalendarIcon, X } from "lucide-react";
import { DateRange } from "react-day-picker";

import { cn } from "../../lib/utils";
import { Button } from "../../components/ui/button";
import { Calendar } from "../../components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "../../components/ui/popover";

import { fr } from "date-fns/locale";
import { Locale } from "date-fns";

interface DateRangePickerProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: DateRange;
  onUpdateFilter: (range: DateRange | undefined) => void;
  align?: "start" | "center" | "end";
  locale?: Locale;
}

export function DateRangePicker({
  className,
  value,
  onUpdateFilter,
  align = "start",
  locale = fr,
}: DateRangePickerProps) {
  // [>]: Use internal state only for in-progress selection (first click before second).
  // Once complete range is selected, parent's `value` prop is the source of truth.
  const [pendingRange, setPendingRange] = React.useState<DateRange | undefined>(
    undefined,
  );

  // [>]: Display pending selection if in progress, otherwise show parent's value.
  const displayedRange = pendingRange ?? value;

  // [>]: Only call onUpdateFilter when range is complete (from AND to) or cleared.
  const handleSelect = (selectedRange: DateRange | undefined) => {
    // [>]: Trigger filter only when:
    // 1. Range is cleared (undefined)
    // 2. Complete range selected (both from and to are set)
    if (!selectedRange || (selectedRange.from && selectedRange.to)) {
      setPendingRange(undefined); // Clear pending, parent value takes over.
      onUpdateFilter(selectedRange);
    } else {
      // [>]: First click only - store in pending state for display.
      setPendingRange(selectedRange);
    }
  };

  // [>]: Clear button handler to reset filter.
  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    setPendingRange(undefined);
    onUpdateFilter(undefined);
  };

  return (
    <div className={cn("grid gap-2", className)}>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant="outline"
            className={cn(
              "w-full justify-start text-left font-normal md:w-[300px]",
              !displayedRange && "text-muted-foreground",
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {displayedRange?.from ? (
              displayedRange.to ? (
                <>
                  {format(displayedRange.from, "LLL dd, y")} -{" "}
                  {format(displayedRange.to, "LLL dd, y")}
                </>
              ) : (
                format(displayedRange.from, "LLL dd, y")
              )
            ) : (
              <span>Sélectionnez une plage de dates</span>
            )}
            {displayedRange && (
              <X
                className="ml-auto h-4 w-4 opacity-50 hover:opacity-100"
                onClick={handleClear}
              />
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align={align}>
          <Calendar
            mode="range"
            defaultMonth={displayedRange?.from ?? subMonths(new Date(), 1)}
            selected={displayedRange}
            onSelect={handleSelect}
            initialFocus
            locale={locale}
            numberOfMonths={2}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}
