import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  
  if (path.startsWith('/admin')) {
    const adminPassword = process.env.ADMIN_PASSWORD;
    
    // Check if admin is authenticated
    const authCookie = request.cookies.get('admin-auth');
    
    if (!authCookie || authCookie.value !== adminPassword) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: '/admin/:path*',
};
