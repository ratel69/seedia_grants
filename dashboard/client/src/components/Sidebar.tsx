import { Link, useLocation } from "wouter";
import { useHashLocation } from "wouter/use-hash-location";
import { BarChart3, List, Sun, Moon, Zap } from "lucide-react";
import { useTheme } from "./ThemeProvider";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/grants", label: "Granty", icon: List },
  { href: "/stats",  label: "Statystyki", icon: BarChart3 },
];

export function Sidebar() {
  const [loc] = useHashLocation();
  const { theme, toggle } = useTheme();

  return (
    <aside className="w-56 shrink-0 h-screen flex flex-col bg-sidebar border-r border-sidebar-border">
      {/* Logo */}
      <div className="flex items-center gap-2 px-5 py-5 border-b border-sidebar-border">
        <div className="w-7 h-7 rounded bg-primary flex items-center justify-center">
          <Zap className="w-4 h-4 text-primary-foreground" />
        </div>
        <div>
          <div className="text-sm font-bold leading-none">SEEDiA</div>
          <div className="text-[10px] text-muted-foreground mt-0.5">Grant Intelligence</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = loc === href || (href === "/grants" && (loc === "/" || loc === ""));
          return (
            <Link key={href} href={href}>
              <a className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                active
                  ? "bg-primary/15 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )}>
                <Icon className="w-4 h-4" />
                {label}
              </a>
            </Link>
          );
        })}
      </nav>

      {/* Theme toggle */}
      <div className="px-3 pb-5">
        <button
          onClick={toggle}
          className="flex items-center gap-3 px-3 py-2 w-full rounded-md text-sm text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
          data-testid="button-theme-toggle"
        >
          {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          {theme === "dark" ? "Jasny motyw" : "Ciemny motyw"}
        </button>
      </div>
    </aside>
  );
}
