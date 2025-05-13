// frontend/components/ui/date-range-picker.tsx
"use client";

import * as React from "react";
import { addDays, format } from "date-fns";
import { Calendar as CalendarIcon } from "lucide-react";
import { DateRange } from "react-day-picker";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

interface DateRangePickerProps extends React.HTMLAttributes<HTMLDivElement> {
  initialDateRange?: DateRange;
  onUpdateFilter: (range: DateRange | undefined) => void;
  align?: "start" | "center" | "end";
}

export function DateRangePicker({
  className,
  initialDateRange,
  onUpdateFilter,
  align = "start",
}: DateRangePickerProps) {
  const [date, setDate] = React.useState<DateRange | undefined>(initialDateRange);
  const [isOpen, setIsOpen] = React.useState(false);

  React.useEffect(() => {
    // If an initial date range is provided, set it.
    if (initialDateRange) {
        setDate(initialDateRange);
    }
  }, [initialDateRange]);

  const handleSelect = (selectedRange: DateRange | undefined) => {
    setDate(selectedRange);
    onUpdateFilter(selectedRange);
    // Optionally close popover on selection, or require explicit close
    // setIsOpen(false); 
  };

  return (
    <div className={cn("grid gap-2", className)}>
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={"outline"}
            className={cn(
              "w-full justify-start text-left font-normal md:w-[300px]", // md:w-[300px] for a decent default width
              !date && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {date?.from ? (
              date.to ? (
                <>
                  {format(date.from, "LLL dd, y")} - {
                    format(date.to, "LLL dd, y")
                  }
                </>
              ) : (
                format(date.from, "LLL dd, y")
              )
            ) : (
              <span>Sélectionnez une plage de dates</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align={align}>
          <Calendar
            initialFocus
            mode="range"
            defaultMonth={date?.from}
            selected={date}
            onSelect={handleSelect}
            numberOfMonths={2}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}
