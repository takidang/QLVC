import { Component, type ReactNode } from 'react'

// React chỉ bắt được lỗi render (như tải file code trang lazy bị lỗi) bằng class component
export default class BatLoiTrang extends Component<{ children: ReactNode }, { loi: boolean }> {
  state = { loi: false }

  static getDerivedStateFromError() {
    return { loi: true }
  }

  render() {
    if (this.state.loi) {
      return (
        <div className="kinh" role="alert">
          <p>Không tải được trang này. Có thể mạng vừa ngắt hoặc hệ thống vừa cập nhật.</p>
          <button onClick={() => window.location.reload()}>Tải lại trang</button>
        </div>
      )
    }
    return this.props.children
  }
}
