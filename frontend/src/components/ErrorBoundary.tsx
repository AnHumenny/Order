import React, { Component, ReactNode } from "react";
import type { Props, State } from "../api/types";


export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(_: Error) {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error("Error caught by ErrorBoundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 20 }}>
          <h3>Что-то пошло не так.</h3>
          <p>Попробуйте обновить страницу или вернуться позже.</p>
        </div>
      );
    }

    return this.props.children;
  }
}
