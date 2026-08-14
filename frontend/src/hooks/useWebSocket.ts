import { useEffect, useRef, useCallback, useState } from 'react';
import type { ServerMessage } from '../types/messages';

export type WSStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export function useWebSocket(
  sessionId: string,
  onMessage: (msg: ServerMessage) => void,
  queryString: string = '',
) {
  const ws = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState<WSStatus>('disconnected');
  const reconnectRef = useRef<ReturnType<typeof setTimeout>>(undefined);
  const onMessageRef = useRef(onMessage);
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    // Declared (not a const arrow fn) so the reconnect scheduling below can call it
    // by hoisted name without referencing a ref during render.
    function connect() {
      setStatus('connecting');
      const socket = new WebSocket(`ws://localhost:8000/ws/${sessionId}${queryString ? `?${queryString}` : ''}`);
      ws.current = socket;

      socket.onopen = () => setStatus('connected');
      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data) as ServerMessage;
          onMessageRef.current(msg);
        } catch (e) { console.error('WS parse error', e); }
      };
      socket.onclose = () => {
        setStatus('disconnected');
        reconnectRef.current = setTimeout(connect, 3000);
      };
      socket.onerror = () => setStatus('error');
    }

    connect();
    return () => {
      clearTimeout(reconnectRef.current);
      ws.current?.close();
    };
  }, [sessionId, queryString]);

  const sendMessage = useCallback((payload: object) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(payload));
    }
  }, []);

  return { status, sendMessage };
}
