"use client"
import { Check, Star } from "lucide-react"
import { cn } from "@/lib/utils"
import { FINGERS, type Student } from "@/lib/demo-data"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Badge } from "@/components/ui/badge"

interface FingerSelectorProps {
  selectedFinger: number | null
  onSelect: (fingerId: number) => void
  student?: Student | null
}

// SVG paths for realistic hand illustration
const LEFT_HAND_PATHS = {
  palm: "M 75 170 Q 60 200 60 240 Q 60 290 80 320 Q 100 350 140 350 Q 180 350 200 320 Q 220 290 220 240 Q 220 200 205 170 L 75 170",
  fingers: [
    // Pinky (leftmost on left hand palm view)
    { id: 9, path: "M 45 170 L 25 130 Q 16 115 18 95 Q 20 75 35 75 Q 50 75 55 100 L 75 170", cx: 35, cy: 90 },
    // Ring
    { id: 8, path: "M 80 170 L 60 95 Q 55 75 60 55 Q 65 35 80 40 Q 95 45 100 70 L 115 170", cx: 80, cy: 55 },
    // Middle
    { id: 7, path: "M 120 170 L 105 75 Q 100 55 105 35 Q 110 15 125 20 Q 140 25 145 55 L 155 170", cx: 125, cy: 40 },
    // Index
    { id: 6, path: "M 160 170 L 150 85 Q 145 70 150 55 Q 155 40 170 45 Q 185 50 185 80 L 190 170", cx: 170, cy: 60 },
    // Thumb (rightmost on left hand palm view)
    {
      id: 5,
      path: "M 215 180 Q 210 170 205 155 Q 195 130 200 110 Q 205 90 220 85 Q 235 80 245 95 Q 255 110 250 130 Q 240 160 215 180",
      cx: 230,
      cy: 100,
    },
  ],
}

const RIGHT_HAND_PATHS = {
  palm: "M 95 170 Q 80 200 80 240 Q 80 290 100 320 Q 120 350 160 350 Q 200 350 220 320 Q 240 290 240 240 Q 240 200 225 170 L 95 170",
  fingers: [
    // Thumb (leftmost on right hand palm view)
    {
      id: 0,
      path: "M 85 180 Q 60 160 50 130 Q 45 110 55 95 Q 65 80 80 85 Q 95 90 100 110 Q 105 130 95 155 Q 90 170 85 180",
      cx: 70,
      cy: 100,
    },
    // Index
    { id: 1, path: "M 110 170 L 115 80 Q 115 50 130 45 Q 145 40 150 55 Q 155 70 150 85 L 140 170", cx: 130, cy: 60 },
    // Middle
    { id: 2, path: "M 145 170 L 155 55 Q 160 25 175 20 Q 190 15 195 35 Q 200 55 195 75 L 180 170", cx: 175, cy: 40 },
    // Ring
    { id: 3, path: "M 185 170 L 200 70 Q 205 45 220 40 Q 235 35 240 55 Q 245 75 240 95 L 220 170", cx: 220, cy: 55 },
    // Pinky (rightmost on right hand palm view)
    { id: 4, path: "M 225 170 L 245 100 Q 250 75 265 75 Q 280 75 282 95 Q 284 115 275 130 L 255 170", cx: 265, cy: 90 },
  ],
}

interface HandIllustrationProps {
  hand: "left" | "right"
  selectedFinger: number | null
  enrolledFingers: number[]
  onFingerClick: (id: number) => void
}

function HandIllustration({ hand, selectedFinger, enrolledFingers, onFingerClick }: HandIllustrationProps) {
  const paths = hand === "left" ? LEFT_HAND_PATHS : RIGHT_HAND_PATHS

  return (
    <div className="flex flex-col items-center">
      <span className="text-sm font-medium text-muted-foreground mb-2 capitalize">{hand} Hand</span>
      <svg viewBox="0 0 300 380" className="w-full max-w-[200px] h-auto">
        {/* Palm */}
        <path d={paths.palm} className="fill-muted/60 transition-colors" />

        {/* Fingers */}
        <TooltipProvider delayDuration={0}>
          {paths.fingers.map((finger) => {
            const fingerInfo = FINGERS.find((f) => f.id === finger.id)
            const isSelected = selectedFinger === finger.id
            const isEnrolled = enrolledFingers.includes(finger.id)
            const isRecommended = fingerInfo?.recommended

            return (
              <Tooltip key={finger.id}>
                <TooltipTrigger asChild>
                  <g onClick={() => onFingerClick(finger.id)} className="cursor-pointer">
                    <path
                      d={finger.path}
                      className={cn(
                        "transition-all duration-200",
                        isSelected
                          ? "fill-primary stroke-primary stroke-[3]"
                          : isEnrolled
                            ? "fill-success/40 stroke-success stroke-2"
                            : "fill-muted/60 hover:fill-muted stroke-transparent",
                      )}
                    />

                    {/* Selection/Enrolled indicator */}
                    {(isSelected || isEnrolled) && (
                      <g transform={`translate(${finger.cx - 10}, ${finger.cy - 10})`}>
                        <circle cx="10" cy="10" r="10" className={isSelected ? "fill-primary" : "fill-success"} />
                        <Check className="text-white" x="3" y="3" width="14" height="14" />
                      </g>
                    )}

                    {/* Recommended indicator */}
                    {isRecommended && !isSelected && !isEnrolled && (
                      <g transform={`translate(${finger.cx - 8}, ${finger.cy - 8})`}>
                        <circle cx="8" cy="8" r="8" className="fill-warning" />
                        <Star
                          className="text-warning-foreground"
                          x="2"
                          y="2"
                          width="12"
                          height="12"
                          fill="currentColor"
                        />
                      </g>
                    )}
                  </g>
                </TooltipTrigger>
                <TooltipContent side="top" className="font-medium">
                  <div className="flex items-center gap-2">
                    {fingerInfo?.name}
                    {isRecommended && (
                      <Badge variant="secondary" className="text-xs">
                        Recommended
                      </Badge>
                    )}
                    {isEnrolled && <Badge className="bg-success/10 text-success border-0 text-xs">Enrolled</Badge>}
                  </div>
                </TooltipContent>
              </Tooltip>
            )
          })}
        </TooltipProvider>
      </svg>
    </div>
  )
}

export function FingerSelector({ selectedFinger, onSelect, student }: FingerSelectorProps) {
  const enrolledFingers = student?.enrolledFingers || []
  const selectedFingerInfo = FINGERS.find((f) => f.id === selectedFinger)

  return (
    <div className="space-y-6">
      {/* Instructions */}
      <div className="text-center">
        <p className="text-sm text-muted-foreground">
          Click on a finger to select it for enrollment.
          <span className="inline-flex items-center gap-1 ml-1">
            <Star className="size-3 text-warning" fill="currentColor" />
            indicates recommended finger.
          </span>
        </p>
      </div>

      {/* Hand Illustrations */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-6 sm:gap-12 p-6 bg-muted/30 rounded-2xl">
        <HandIllustration
          hand="left"
          selectedFinger={selectedFinger}
          enrolledFingers={enrolledFingers}
          onFingerClick={onSelect}
        />
        <div className="hidden sm:block w-px h-48 bg-border" />
        <HandIllustration
          hand="right"
          selectedFinger={selectedFinger}
          enrolledFingers={enrolledFingers}
          onFingerClick={onSelect}
        />
      </div>

      <div className="flex flex-wrap justify-center gap-2">
        {FINGERS.map((finger) => {
          const isSelected = selectedFinger === finger.id
          const isEnrolled = enrolledFingers.includes(finger.id)

          return (
            <button
              key={finger.id}
              onClick={() => onSelect(finger.id)}
              className={cn(
                "px-3 py-1.5 rounded-full text-xs font-medium transition-all border",
                isSelected
                  ? "border-primary bg-primary text-primary-foreground shadow-md scale-105"
                  : isEnrolled
                    ? "border-success/50 bg-success/10 text-success"
                    : "border-border bg-card hover:border-primary/50 text-muted-foreground hover:text-foreground",
              )}
            >
              {finger.name}
              {isEnrolled && !isSelected && " ✓"}
            </button>
          )
        })}
      </div>
    </div>
  )
}
