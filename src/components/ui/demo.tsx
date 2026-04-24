import {
  GlassCard,
  GlassCardHeader,
  GlassCardTitle,
  GlassCardContent,
  GlassCardDescription,
  GlassCardAction,
  GlassCardFooter,
} from "@/components/ui/glass-card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"

export default function DemoOne() {
  return (
    <div className="bg-[url(https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=2670&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)] w-full h-screen flex items-center justify-center bg-cover bg-center">
      <GlassCard className="w-full max-w-sm">
        <GlassCardHeader>
          <GlassCardTitle>Login to your account</GlassCardTitle>
          <GlassCardDescription>
            Enter your email below to login to your account
          </GlassCardDescription>
          <GlassCardAction>
            <Button variant="link" asChild>
              <a href="https://moleculeui.design" target="_blank" rel="noreferrer">
                Sign Up
              </a>
            </Button>
          </GlassCardAction>
        </GlassCardHeader>
        <GlassCardContent>
          <form>
            <div className="flex flex-col gap-6">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  required
                />
              </div>
              <div className="grid gap-2">
                <div className="flex items-center">
                  <Label htmlFor="password">Password</Label>
                  <a
                    href="https://moleculeui.design"
                    className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                  >
                    Forgot your password?
                  </a>
                </div>
                <Input id="password" type="password" required />
              </div>
            </div>
          </form>
        </GlassCardContent>
        <GlassCardFooter className="flex-col gap-2">
          <Button type="submit" className="w-full" asChild>
            <a href="https://moleculeui.design" target="_blank" rel="noreferrer">
              Login
            </a>
          </Button>
          <Button variant="ghost" className="w-full" asChild>
            <a href="https://moleculeui.design" target="_blank" rel="noreferrer">
              Login with Google
            </a>
          </Button>
        </GlassCardFooter>
      </GlassCard>
    </div>
  )
}