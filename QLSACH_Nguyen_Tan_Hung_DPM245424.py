import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="LocalHost",
        user="root",
        password="@HUNGVN1234",
        database="QLSach",

    )

def check_maloai_trung(ket_noi, matheloai):
    # Kiểm tra xem mã thể loại (MaTheLoai) có đã tồn tại trong bảng TheLoai hay không
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT COUNT(*) FROM TheLoai WHERE MaTheLoai = %s", (matheloai,))
    result = con_tro.fetchone()[0]
    return result > 0  # True nếu trùng

def check_masach_trung(ket_noi, masach):
    # Kiểm tra xem mã sách (MaSach) tương tự như check loại
    con_tro = ket_noi.cursor()
    con_tro.execute("SELECT COUNT(*) FROM Sach WHERE MaSach = %s", (masach,))
    result = con_tro.fetchone()[0]
    return result > 0 

# KHỞI TẠO CỬA SỔ
root = tk.Tk()
root.title("Quản Lý Sách")
def center_window(cua_so, w=850, h=500):
    # Căn giữa cửa sổ 'cua_so' trên màn hình với kích thước w x h (hàm tiện ích UI)
    ws = cua_so.winfo_screenwidth()
    hs = cua_so.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    cua_so.geometry(f'{w}x{h}+{x}+{y}')
    cua_so.resizable(True, True)
center_window(root)

# HÀM XÓA NỘI DUNG MÀN HÌNH
khung = tk.Frame(root)
khung.pack(fill=tk.BOTH, expand=True)
def clear_frame():
    # Xóa mọi widget con trong khung chính 'khung' để chuẩn bị vẽ màn hình mới
    for w in khung.winfo_children():
        w.destroy()


# MÀN HÌNH DANH SÁCH

def show_danh_sach():
    # Hàm tải dữ liệu thể loại vào bộ lọc
    def taidulieu_loai():
        # Tải dữ liệu các thể loại từ DB và cập nhật vào bộ lọc
        try:
            connect = get_connection()
            contro = connect.cursor()
            contro.execute("SELECT TenTheLoai FROM TheLoai")
            rows = contro.fetchall()
            connect.close()
        except Exception as ex:
            # Có thể thiếu bảng hoặc gặp lỗi kết nối cơ sở dữ liệu; bỏ qua
            # Tránh làm ứng dụng bị treo — chỉ thông báo cho người dùng một lần
            try:
                messagebox.showwarning("Thông báo", f"Không thể tải thể loại: {ex}")
            except Exception as ex:
                print("Lỗi khi hiển thị cảnh báo thể loại:", ex)
            rows = []

        values = ["Tất cả"] + [r[0] for r in rows]
        try:
            bo_loc_loai['values'] = values
            if len(values) > 0:
                bo_loc_loai.current(0)
        except Exception:
            pass



# Hàm tải dữ liệu sách vào Bảng
    def taidulieu_sach():
        # Tải danh sách sách từ DB theo bộ lọc và ô tìm kiếm, sau đó hiển thị vào Bảng chính
        connect = get_connection()
        contro = connect.cursor()

        Tim_kiem = thanh_tim_kiem.get()
        loc_loai = bo_loc_loai.get()

        Thongtin = []
        # Chỉ hiển thị
        dulieu = '''SELECT s.MaSach, s.TenSach, tl.TenTheLoai, s.DonGia
            FROM Sach s
            JOIN TheLoai tl ON s.MaTheLoai = tl.MaTheLoai
            WHERE 1=1'''
        
        if Tim_kiem.strip() != "":
            dulieu += " AND (s.TenSach LIKE %s OR MaSach LIKE %s)"
            Thongtin += [f'%{Tim_kiem}%'] * 2

        if loc_loai != "Tất cả":
            dulieu += " AND tl.TenTheLoai = %s"
            Thongtin.append(loc_loai)
        
        contro.execute(dulieu, Thongtin)
        rs = contro.fetchall()

        tree.delete(*tree.get_children())

        for r in rs:
            clean_row = [col if not isinstance(col, tuple) else col[0] for col in r]
            tree.insert("", "end", values=clean_row + ["[...]"])

        connect.close()


    def Them_sach():
        # Mở cửa sổ để nhập thông tin sách mới (gồm MaSach, TenSach, MaTacGia, MaTheLoai, MaNXB, DonGia)
        cuaSo = tk.Toplevel(root)
        cuaSo.title("Thêm sách")
        cuaSo.geometry("350x400")
        # ======= UI Thêm =======
        tk.Label(cuaSo, text="Mã sách:").pack() # Nhập mã sách
        ma = tk.Entry(cuaSo, width=30)
        ma.pack()
        tk.Label(cuaSo, text="Tên sách:").pack() # Nhập tên sách
        ten = tk.Entry(cuaSo,width=30)
        ten.pack()
        tk.Label(cuaSo, text="Mã tác giả:").pack() # Nhập mã tác giả
        tg = tk.Entry(cuaSo,width=30)
        tg.pack()
        tk.Label(cuaSo, text="Mã thể loại:").pack() # Nhập mã thể loại
        tl = tk.Entry(cuaSo,width=30)
        tl.pack()
        tk.Label(cuaSo, text="Mã NXB:").pack() # Nhập mã NXB
        nxb = tk.Entry(cuaSo,width=30)
        nxb.pack()
        tk.Label(cuaSo, text="Đơn giá:").pack() # Nhập đơn giá
        dg = tk.Entry(cuaSo,width=30)
        dg.pack()
        tk.Label(cuaSo, text="So lượng:").pack() # Nhập số lượng
        sl = tk.Entry(cuaSo,width=30)
        sl.pack()

        def add_book(): # Lưu sách vào database
            # Lưu sách mới vào bảng Sach: kiểm tra trùng mã
            connect = get_connection()
            contro = connect.cursor()
            if check_masach_trung(connect, ma.get()):
                messagebox.showerror("Lỗi", "Mã sách đã tồn tại")
                cuaSo.destroy()
                return
            contro.execute(""" INSERT INTO Sach (MaSach, TenSach, MaTacGia, MaTheLoai, MaNXB, DonGia, SoLuongTon) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", (ma.get(), ten.get(), tg.get(), tl.get(), nxb.get(), float(dg.get()), int(sl.get())))
            connect.commit()
            messagebox.showinfo("Thành công", "Đã thêm sách")
            cuaSo.destroy()
            # làm mới danh sách sách
            taidulieu_sach()
        tk.Button(cuaSo, text="Thêm", command=add_book).pack(pady=10)

    # Hộp thoại kết hợp để chỉnh sửa và xóa sách
    def ql_sach():
        cuaSo = tk.Toplevel(root)
        cuaSo.title("Quản lý sách - Chỉnh sửa / Xóa")
        cuaSo.geometry("380x420")
        cuaSo.resizable(True, True)
        tk.Label(cuaSo, text="Nhập mã sách (để tải / xóa):").pack(pady=(6,0))
        xoa_tim = tk.Entry(cuaSo)
        xoa_tim.pack(pady=4)
        # Các trường để chỉnh sửa
        tk.Label(cuaSo, text="Tên sách:").pack()
        ten = tk.Entry(cuaSo)
        ten.pack()
        tk.Label(cuaSo, text="Mã tác giả:").pack()
        tg = tk.Entry(cuaSo)
        tg.pack()
        tk.Label(cuaSo, text="Mã thể loại:").pack()
        tl = tk.Entry(cuaSo)
        tl.pack()
        tk.Label(cuaSo, text="Mã NXB:").pack()
        nxb = tk.Entry(cuaSo)
        nxb.pack()
        tk.Label(cuaSo, text="Đơn giá:").pack()
        dg = tk.Entry(cuaSo)
        dg.pack()

        # tải dữ liệu
        def load_book():
            connect = None
            try:
                connect = get_connection(); contro = connect.cursor()
                contro.execute("SELECT TenSach, MaTacGia, MaTheLoai, MaNXB, DonGia FROM Sach WHERE MaSach = %s", (xoa_tim.get(),))
                row = contro.fetchone()
                if not row:
                    messagebox.showerror("Lỗi", "Không tìm thấy sách")
                    return
                ten.delete(0, tk.END); ten.insert(0, row[0])
                tg.delete(0, tk.END); tg.insert(0, row[1])
                tl.delete(0, tk.END); tl.insert(0, row[2])
                nxb.delete(0, tk.END); nxb.insert(0, row[3])
                dg.delete(0, tk.END); dg.insert(0, row[4])
            except Exception as ex:
                messagebox.showerror("Lỗi", f"Không thể tải sách: {ex}")
            finally:
                connect.close()

        # cập nhật
        def update_book():
            if not xoa_tim.get().strip():
                messagebox.showwarning("Lỗi", "Nhập mã sách để cập nhật")
                return
            try:
                connect = get_connection(); contro = connect.cursor()
                contro.execute("""
                    UPDATE Sach
                    SET TenSach = %s, MaTacGia = %s, MaTheLoai = %s, MaNXB = %s, DonGia = %s
                    WHERE MaSach = %s
                """, (ten.get(), tg.get(), tl.get(), nxb.get(), float(dg.get()), xoa_tim.get()))
                connect.commit()
                messagebox.showinfo("Thành công", "Đã cập nhật sách")
                cuaSo.destroy(); taidulieu_sach()
            except Exception as ex:
                messagebox.showerror("Lỗi", f"Không thể cập nhật sách: {ex}")
            finally:
                    if connect:
                        try:
                            connect.close()
                        except Exception as ex:
                            print("Lỗi khi đóng kết nối (update/delete sách):", ex)

        # xóa
        def delete_book():
            # Xóa sách khỏi DB theo mã sách nhập vào
            if not xoa_tim.get().strip():
                messagebox.showwarning("Lỗi", "Nhập mã sách để xóa")
                return
            if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa sách '{xoa_tim.get()}'?"): 
                return
            try:
                connect = get_connection(); contro = connect.cursor()
                # Xóa chi tiết đơn hàng liên quan đến sách này trước
                contro.execute("DELETE FROM ChiTietDonHang WHERE MaSach = %s", (xoa_tim.get(),))
                # Sau đó xóa sách
                contro.execute("DELETE FROM Sach WHERE MaSach = %s", (xoa_tim.get(),))
                connect.commit()
                messagebox.showinfo("Thành công", "Đã xóa sách")
                cuaSo.destroy(); taidulieu_sach()
            except Exception as ex:
                messagebox.showerror("Lỗi", f"Không thể xóa sách: {ex}")
            finally:
                if connect:
                    try:
                        connect.close()
                    except Exception as ex:
                        print("Lỗi khi đóng kết nối (xóa sách):", ex)

        # các nút
        hangnut = tk.Frame(cuaSo)
        hangnut.pack(pady=12)
        tk.Button(hangnut, text="Tải dữ liệu", command=load_book).pack(side="left", padx=6)
        tk.Button(hangnut, text="Lưu thay đổi", command=update_book).pack(side="left", padx=6)
        tk.Button(hangnut, text="Xoá sách", command=delete_book).pack(side="left", padx=6)



    # Hàm mở cửa sổ chi tiết sách
    def chi_tiet(event):

        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        col = tree.identify_column(event.x)
        row = tree.identify_row(event.y)

        if col == "#5":  # Cột "Xem"
            chon = tree.item(row, "values")
            if chon:
                ma_sach = chon[0]
                mo_chitiet(ma_sach)

    # Hàm mở cửa sổ chi tiết sách            
    def mo_chitiet(ma_sach):
        cuaSo = tk.Toplevel(root)
        cuaSo.title("Thông tin chi tiết sách")
        cuaSo.geometry("400x300")
        connect = get_connection()
        contro = connect.cursor()
        contro.execute("""
            SELECT s.MaSach, s.TenSach, tg.TenTacGia, tl.TenTheLoai, nxb.TenNXB, s.DonGia, cts.SoLuong
            FROM Sach s, TacGia tg, TheLoai tl, NhaXuatBan nxb, ChiTietDonHang cts
            WHERE s.MaTacGia = tg.MaTacGia AND s.MaTheLoai = tl.MaTheLoai AND s.MaNXB = nxb.MaNXB AND s.MaSach = cts.MaSach
            AND s.MaSach = %s
        """, (ma_sach,))

        row = contro.fetchone()

        if not row:
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin sách")
            contro.close()
            connect.close()
            cuaSo.destroy()
            return

        labels = [
            "Mã sách: " + str(row[0]),
            "Tên sách: " + str(row[1]),
            "Tác giả: " + str(row[2]),
            "Thể loại: " + str(row[3]),
            "Nhà xuất bản: " + str(row[4]),
            "Đơn giá: " + str(row[5]),
            "Số Lượng: " + str(row[6]),
        ]
        for text in labels:
            tk.Label(cuaSo, text=text, anchor="w").pack(fill="x", padx=10, pady=3)
        
        contro.close()
        connect.close()

    clear_frame()
    # Thanh khungtop control
    khungtop = tk.Frame(khung)
    khungtop.pack(fill="x", pady=5)


    # --- TÌM KIẾM ---
    tk.Label(khungtop, text="Tìm kiếm:").pack(side="left", padx=5)
    thanh_tim_kiem = tk.Entry(khungtop, width=30)
    thanh_tim_kiem.pack(side="left")

    tk.Button(khungtop, text="Search", command=taidulieu_sach).pack(side="left", padx=5)


    # --- LỌC THỂ LOẠI ---
    tk.Label(khungtop, text="Lọc thể loại:").pack(side="left", padx=10)
    bo_loc_loai = ttk.Combobox(khungtop, width=20, state="readonly")
    bo_loc_loai.pack(side="left")
    bo_loc_loai.bind("<<ComboboxSelected>>", lambda e:taidulieu_sach())



    # --- CÁC NÚT ---
    frame_nut = tk.Frame(khung)
    frame_nut.pack(fill="x", pady=5)

    tk.Button(frame_nut, text="Thêm sách",command = Them_sach, width=15).pack(side="left", padx=10)
    tk.Button(frame_nut, text="Chỉnh sửa / Xóa", command = ql_sach, width=20).pack(side="left", padx=10)
    # (Thêm thể loại moved to 'Thông tin Phụ')
    # --- BẢNG DANH SÁCH ---
    frame_bang = tk.Frame(khung)
    frame_bang.pack(fill="both", expand=True)

    columns = ("ma", "ten", "loai", "gia", "xem")
    tree = ttk.Treeview(frame_bang, columns=columns, show="headings")

    tree.heading("ma", text="Mã sách")
    tree.heading("ten", text="Tên sách")
    tree.heading("loai", text="Thể loại")
    tree.heading("gia", text="Đơn giá")
    tree.heading("xem", text="Xem")

    tree.column("ma", width=120)
    tree.column("ten", width=350)
    tree.column("loai", width=150)
    tree.column("gia", width=120)
    tree.column("xem", width=80)
    tree.bind("<Button-1>", chi_tiet)
    tree.pack(fill="both", expand=True)

    # Tải ban đầu: điền thể loại và bảng khi view được hiển thị
    taidulieu_loai()
    taidulieu_sach()
    


#MÀN HÌNH BÁN SÁCH
def show_ban_sach():

    clear_frame()

    # Khung trên
    khungtop = tk.Frame(khung)
    khungtop.pack(fill="both", expand=True, padx=5, pady=5)

    # =============== KHUNG TÌM SÁCH ===============
    tim = tk.LabelFrame(khungtop)
    tim.pack(fill="x", padx=10, pady=5)

    tk.Label(tim, text="Tên sách:").pack(side="left", padx=5)
    tim_sach_ban = tk.Entry(tim, width=30)
    tim_sach_ban.pack(side="left", padx=5)

    # =============== NỘI DUNG CHÍNH ===============
    frame_giua = tk.Frame(khungtop)
    frame_giua.pack(fill="both", expand=True, padx=10, pady=5)

    # Khung bên trái: danh sách sách
    frameleft = tk.LabelFrame(frame_giua, text="Danh sách sách")
    frameleft.pack(side="left", fill="both", expand=True, padx=(0, 6))

    bang_sach = ttk.Treeview(frameleft, columns=("MaSach", "TenSach", "DonGia", "SoLuongTon"), show="headings", height=12)
    bang_sach.heading("MaSach", text="Mã sách")
    bang_sach.heading("TenSach", text="Tên sách")
    bang_sach.heading("DonGia", text="Đơn giá")
    bang_sach.column("DonGia", width=80)
    bang_sach.column("SoLuongTon", width=80)
    bang_sach.pack(fill="both", expand=True)


    # Khung bên phải: giỏ hàng
    frameright = tk.Frame(frame_giua)
    frameright.pack(side="left", fill="y")

    gio_frame = tk.LabelFrame(frameright, text="Giỏ hàng")
    gio_frame.pack(fill="both", expand=False)

    gio_hang = ttk.Treeview(gio_frame, columns=("MaSach", "TenSach", "SoLuong", "DonGia", "ThanhTien"),show="headings")
    gio_hang.heading("MaSach", text="Mã sách")
    gio_hang.heading("TenSach", text="Tên sách")
    gio_hang.heading("SoLuong", text="Số lượng")
    gio_hang.heading("DonGia", text="Đơn giá")
    gio_hang.heading("ThanhTien", text="Thành tiền")
    gio_hang.column("SoLuong", width=70)
    gio_hang.column("DonGia", width=80)
    gio_hang.column("ThanhTien", width=120)
    gio_hang.pack(fill="both", expand=True)

    # =============== CHỨC NĂNG GIỎ HÀNG  ===============
    hanh_dong_dat = tk.Frame(frameright)
    hanh_dong_dat.pack(fill="x", padx=6, pady=(8, 4))

    tk.Label(hanh_dong_dat, text="Số lượng:").pack(side="left")
    soluongban = tk.Entry(hanh_dong_dat, width=5)
    soluongban.pack(side="left", padx=5)
    soluongban.insert(0, "1")

    # ===== Các hàm lồng nhau (sử dụng các widget đã tạo bên trên) =====
    def tim_sach():
        # Tìm sách trong bảng Sach theo tên hoặc mã trong khung bán hàng
        for row in bang_sach.get_children():
            bang_sach.delete(row)
        connect = get_connection()
        contro = connect.cursor()
        contro.execute("""SELECT MaSach, TenSach, DonGia, IFNULL(SoLuongTon, 0) FROM Sach 
        WHERE (TenSach LIKE %s OR MaSach LIKE %s)""", ( f'%{tim_sach_ban.get()}%', f'%{tim_sach_ban.get()}%'))
        rows = contro.fetchall()
        for row in rows:
            clean = [col if not isinstance(col, tuple) else col[0] for col in row]
            bang_sach.insert("", "end", values=clean)
        connect.close()
        
    def them_vo_gio():
        # Thêm sách đã chon từ danh sách vào giỏ hàng, tính tiền tạm thời và kiểm tra tồn kho
        chon = bang_sach.focus()
        if not chon:
            messagebox.showwarning("Lỗi", "Hãy chon sách.")
            return

        ma, ten, gia, kho = bang_sach.item(chon, "values")
        try:
            slm = int(soluongban.get())
        except Exception:
            messagebox.showerror("Lỗi", "Số lượng không hợp lệ")
            return
        # kiểm tra tồn kho nếu có dữ liệu
        try:
            available = int(kho)
            if slm > available:
                messagebox.showerror("Lỗi", f"Không đủ hàng trong kho (còn {available})")
                return
        except Exception:
            # nếu không thể chuyển 'kho' thành số (thiếu) thì bỏ qua
            pass
        thanh_tien = slm * float(gia)

        gio_hang.insert("", "end", values=(ma, ten, slm, float(gia), thanh_tien))
        # cập nhật nhãn tổng được hiển thị
        capnhat_tt()


    def xoa_khoi_gio():
        # Xóa mục đang chon khỏi giỏ hàng
        chon = gio_hang.focus()
        if chon:
            gio_hang.delete(chon)
            capnhat_tt()


    # Tăng hoặc giảm số lượng cho mục đang chọn trong giỏ
    def sl_thaydoi(thaydoi):
        # Thay đổi số lượng của mục đang chọn trong giỏ hàng (tăng / giảm) và cập nhật tổng
        sel = gio_hang.focus()
        if not sel:
            messagebox.showwarning("Lỗi", "Chọn mục trong giỏ để sửa số lượng")
            return
        ma, ten, so_luong, don_gia, thanh_tien = gio_hang.item(sel, "values")
        try:
            so_luong = int(so_luong)
            don_gia = float(don_gia)
        except Exception:
            messagebox.showerror("Lỗi", "Dữ liệu số lượng/đơn giá không hợp lệ")
            return
        new_slm = so_luong + thaydoi
        if new_slm <= 0:
            gio_hang.delete(sel)
        else:
            new_total = new_slm * don_gia
            gio_hang.item(sel, values=(ma, ten, new_slm, don_gia, new_total))
            capnhat_tt()

    def capnhat_tt():
        # Tính lại tổng tiền hiện tại trong giỏ và cập nhật nhãn hiển thị
        total = 0.0
        for item in gio_hang.get_children():
            vals = gio_hang.item(item, "values")
            try:
                total += float(vals[4])
            except Exception:
                pass
        try:
            tong_tien.config(text=f"Tổng: {total:,.2f}")
        except Exception:
            pass

    def kiemtra():
        # Xử lý thanh toán: kiểm tra tồn kho, lưu DonHang + ChiTietDonHang và cập nhật tồn kho trong DB
        if not gio_hang.get_children(): 
            messagebox.showerror("Lỗi", "Giỏ hàng trống.") 
            return
        connect = get_connection(); contro = connect.cursor()
        items = []
        tong_tien = 0.0
        # Kiểm tra hợp lệ các mục trong giỏ và tồn kho
        for it in gio_hang.get_children():
            ma, ten, so_luong, don_gia, thanh = gio_hang.item(it, "values")
            try:
                slm = int(so_luong); dgm = float(don_gia); total_item = float(thanh)
            except Exception:
                messagebox.showerror("Lỗi", "Dữ liệu trong giỏ không hợp lệ")
                connect.close(); return
            contro.execute("SELECT IFNULL(SoLuongTon, 0) FROM Sach WHERE MaSach = %s", (ma,))
            row = contro.fetchone()
            available = int(row[0]) if row and row[0] is not None else 0
            if slm > available:
                messagebox.showerror("Lỗi", f"Sách {ma} - {ten}: chỉ còn {available}, không thể bán {slm}.")
                connect.close(); return
            items.append((ma, slm, dgm, total_item))
            tong_tien += total_item
        # Tạo mã đơn hàng và chèn đơn hàng
        contro.execute("SELECT COUNT(*) FROM DonHang")
        dem = contro.fetchone()[0] + 1
        ma_dh = f"DH{dem:03d}"
        kh = khach.get().strip() if 'khach' in locals() or 'khach' in globals() else 'Khách Lẻ'
        if kh == "": kh = "Khách Lẻ"
        contro.execute("INSERT INTO DonHang (MaDonHang, NgayLap, TenKhachHang, TongTien) VALUES (%s, NOW(), %s, %s)", (ma_dh, kh, tong_tien))
        # Chèn chi tiết đơn hàng và giảm tồn kho cho từng mục
        for ma_sach, slm, dgm, total_item in items:
            contro.execute("INSERT INTO ChiTietDonHang (MaDonHang, MaSach, SoLuong, DonGia) VALUES (%s, %s, %s, %s)", (ma_dh, ma_sach, slm, float(dgm)))
            # Giảm tồn kho cho sách này
            contro.execute("UPDATE Sach SET SoLuongTon = IFNULL(SoLuongTon, 0) - %s WHERE MaSach = %s", (slm, ma_sach))
        # Cập nhật tổng đơn hàng một lần (câu SQL này không cần tham số)
        contro.execute("UPDATE DonHang dh SET TongTien = (SELECT SUM(SoLuong * DonGia) FROM ChiTietDonHang WHERE MaDonHang = dh.MaDonHang)")
        connect.commit(); connect.close()
        messagebox.showinfo("Thành công", f"Đã thanh toán hoá đơn {ma_dh}")
        # Làm mới danh sách và xóa giỏ hàng
        show_danh_sach()
        for it in gio_hang.get_children():
            gio_hang.delete(it)
        try: capnhat_tt()
        except Exception as ex:
            print("Lỗi khi cập nhật tổng tiền (capnhat_tt):", ex)

    # ===== Các control được gắn với hàm =====
    tk.Button(tim, text="Tìm", command=tim_sach).pack(side="left", padx=5)
    tk.Button(hanh_dong_dat, text="Thêm vào giỏ", command=them_vo_gio).pack(side="left", padx=5)
    tk.Button(hanh_dong_dat, text="Xoá khỏi giỏ", command=xoa_khoi_gio).pack(side="left", padx=5)
    tk.Button(hanh_dong_dat, text="+", width=3, command=lambda: sl_thaydoi(1)).pack(side="left", padx=2)
    tk.Button(hanh_dong_dat, text="-", width=3, command=lambda: sl_thaydoi(-1)).pack(side="left", padx=2)

    # Khu thông tin khách hàng và tổng tiền (ở góc phải, phía dưới)
    khung_thao_tac = tk.Frame(frameright)
    khung_thao_tac.pack(fill="x", padx=6, pady=(4,8))
    tk.Label(khung_thao_tac, text="Tên khách hàng:").pack(side="left", padx=(0,6))
    khach = tk.Entry(khung_thao_tac, width=30)
    khach.pack(side="left")

    tong_tien = tk.Label(khung_thao_tac, text="Tổng: 0.00", font=(None, 11, "bold"))
    tong_tien.pack(side="right", padx=6)

    tk.Button(frameright, text="Thanh toán", command=kiemtra).pack(pady=6)
    
    # Tải danh sách sách ban đầu
    tim_sach()


# MÀN HÌNH BÁO CÁO
def show_bao_cao():
    # Hiển thị màn hình báo cáo: doanh thu theo ngày và báo cáo tồn kho, với các chức năng tải dữ liệu
    clear_frame()


    # Doanh thu --- điều khiển + bảng
    frame_rev = ttk.LabelFrame(khung, text="Báo cáo doanh thu (theo ngày)")
    frame_rev.pack(fill="x", padx=10, pady=6)

    dk = ttk.Frame(frame_rev)
    dk.pack(fill="x", padx=6, pady=6)
    ttk.Label(dk, text="Năm:").pack(side="left", padx=(2, 4))
    e_year = ttk.Entry(dk, width=10); e_year.pack(side="left", padx=(0,8)); e_year.insert(0, "2025")
    ttk.Label(dk, text="Tháng (0 = cả năm):").pack(side="left", padx=(2, 4))
    e_month = ttk.Entry(dk, width=10); e_month.pack(side="left", padx=(0,8)); e_month.insert(0, "0")
    tai_bc = ttk.Button(dk, text="Tải báo cáo")
    tai_bc.pack(side="left", padx=6)

    bang_doanhthu = ttk.Treeview(frame_rev, columns=("Ngay", "DoanhThu"), show="headings", height=8)
    bang_doanhthu.heading("Ngay", text="Ngày")
    bang_doanhthu.heading("DoanhThu", text="Doanh thu")
    bang_doanhthu.column("DoanhThu", anchor="e", width=140)
    bang_doanhthu.pack(fill="both", expand=True, padx=6, pady=(6,10))


    def tai_doanh_thu():
        # Tải dữ liệu doanh thu từ DB theo năm/tháng và hiển thị trong bảng doanh thu
        for r in bang_doanhthu.get_children():
            bang_doanhthu.delete(r)
        try:
            year = int(e_year.get())
            month = int(e_month.get())
        except Exception:
            messagebox.showerror("Lỗi", "Năm hoặc tháng không hợp lệ")
            return
        connect = None
        try:
            connect = get_connection(); contro = connect.cursor()
            if month == 0:
                contro.execute("""
                SELECT DATE(NgayLap) AS Ngay, SUM(TongTien) AS DoanhThu FROM DonHang
                WHERE YEAR(NgayLap) = %s
                GROUP BY DATE(NgayLap)
                ORDER BY Ngay
                """, (year,))
            else:
                contro.execute("""
                SELECT DATE(NgayLap) AS Ngay, SUM(TongTien) AS DoanhThu FROM DonHang
                WHERE YEAR(NgayLap) = %s AND MONTH(NgayLap) = %s
                GROUP BY DATE(NgayLap)
                ORDER BY Ngay
                """, (year, month))

            for day, rev in contro.fetchall():
                bang_doanhthu.insert("", "end", values=(str(day), rev))
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Không thể tải báo cáo doanh thu: {ex}")
        finally:
            if connect:
                connect.close()
    tai_bc.config(command=tai_doanh_thu)

    # Tồn kho --- danh sách + nút tải
    khung_kho = ttk.LabelFrame(khung, text="Báo cáo tồn kho")
    khung_kho.pack(fill="both", padx=10, pady=6, expand=True)

    bang_kho = ttk.Treeview(khung_kho, columns=("MaSach", "TenSach", "SoLuong", "TrangThai"), show="headings", height=8)
    bang_kho.heading("MaSach", text="Mã sách")
    bang_kho.heading("TenSach", text="Tên sách")
    bang_kho.heading("SoLuong", text="Tồn kho")
    bang_kho.heading("TrangThai", text="Trạng thái")
    bang_kho.column("SoLuong", width=80)
    bang_kho.column("TrangThai", width=120)
    bang_kho.pack(fill="both", expand=True, padx=6, pady=(6,10))

    def taidl_kho():
        # Tải dữ liệu tồn kho từ DB và hiển thị trong bảng tồn kho, đánh dấu cảnh báo nếu tồn thấp
        for r in bang_kho.get_children():
            bang_kho.delete(r)
        connect = None
        try:
            connect = get_connection(); contro = connect.cursor()
            contro.execute("SELECT MaSach, TenSach, IFNULL(SoLuongTon, 0) as SoLuongTon FROM Sach")
            for ma, ten, sl in contro.fetchall():
                try:
                    sl_int = int(sl)
                except Exception:
                    sl_int = 0
                trang_thai = "Bình thường"; tag = ""
                if sl_int < 10:
                    trang_thai = "Cảnh báo"; tag = "low"
                bang_kho.insert("", "end", values=(ma, ten, sl_int, trang_thai), tags=(tag,))
            bang_kho.tag_configure("low", foreground="red")
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Không thể tải tồn kho: {ex}")
        finally:
            if connect:
                connect.close()
    ttk.Button(khung_kho, text="Tải tồn kho", command=taidl_kho).pack(pady=(0,8))
    

    # Tải báo cáo doanh thu và tồn kho ban đầu
    tai_doanh_thu()
    taidl_kho()


# Thông tin phụ - tác giả, NXB
def show_thong_tin_phu():
    # Màn hình quản lý thông tin phụ: bao gồm tác giả, thể loại và nhà xuất bản (NXB)
    clear_frame()

    def tai_tg():
        # Tải toàn bộ tác giả từ DB và hiển thị trong bảng tác giả
        for r in bang_tg.get_children():
            bang_tg.delete(r)
        try:
            connect = get_connection(); contro = connect.cursor()
            contro.execute("SELECT MaTacGia, TenTacGia FROM TacGia")
            for ma, ten in contro.fetchall():
                clean_ma = ma[0] if isinstance(ma, tuple) else ma
                clean_ten = ten[0] if isinstance(ten, tuple) else ten
                bang_tg.insert("", "end", values=(clean_ma, clean_ten))
        except Exception as ex:
            try:
                messagebox.showwarning("Thông báo", f"Không thể tải danh sách tác giả: {ex}")
            except Exception:
                pass
        finally:
            try:
                connect.close()
            except Exception:
                pass

    # Hàm trợ giúp: kiểm tra mã tác giả trùng
    def check_matacgia_trung(connect, mata):
        # Kiểm tra xem mã tác giả đã tồn tại trong bảng TacGia hay chưa (dùng trước khi thêm)
        contro = connect.cursor()
        contro.execute("SELECT COUNT(*) FROM TacGia WHERE MaTacGia = %s", (mata,))
        result = contro.fetchone()[0]
        return result > 0

    # Các điều khiển ở phần trên
    khungtop = tk.Frame(khung)
    khungtop.pack(fill="x", pady=5)



    # Nút Thêm tác giả
    def them_tac_gia():
        # Mở dialog để thêm một tác giả mới (MaTacGia, TenTacGia)
        cuaSo = tk.Toplevel(root)
        cuaSo.title("Thêm tác giả")
        cuaSo.geometry("320x170")
        tk.Label(cuaSo, text="Mã tác giả:").pack(pady=(8, 0))
        ma = tk.Entry(cuaSo, width=36)
        ma.pack(pady=4)
        tk.Label(cuaSo, text="Tên tác giả:").pack(pady=(8, 0))
        ten = tk.Entry(cuaSo, width=36)
        ten.pack(pady=4)
        def save_tg():
            ma = ma.get().strip()
            ten = ten.get().strip()
            if not ma or not ten:
                messagebox.showwarning("Lỗi", "Mã hoặc tên tác giả không được để trống")
                return
            try:
                connect = get_connection(); contro = connect.cursor()
                if check_matacgia_trung(connect, ma):
                    messagebox.showerror("Lỗi", "Mã tác giả đã tồn tại")
                    return
                contro.execute("INSERT INTO TacGia (MaTacGia, TenTacGia) VALUES (%s, %s)", (ma, ten))
                connect.commit()
                messagebox.showinfo("Thành công", "Đã thêm tác giả")
                cuaSo.destroy()
                tai_tg()
            except Exception as ex:
                messagebox.showerror("Lỗi", f"Không thể thêm tác giả: {ex}")
            finally:
                if connect:
                    try:
                        connect.close()
                    except Exception as ex:
                        print("Lỗi khi đóng kết nối (thêm tác giả):", ex)
        tk.Button(cuaSo, text="Thêm", width=12, command=save_tg).pack(pady=10)
    tk.Button(khungtop, text="Thêm tác giả", command=them_tac_gia, width=16).pack(side="right", padx=8)

    # Khu nội dung
    tbl_frame = tk.Frame(khung)
    tbl_frame.pack(fill="both", expand=True, padx=6, pady=6)

    frameleft = tk.Frame(tbl_frame)
    frameleft.pack(side="left", fill="both", expand=True, padx=(0, 3))

    frameright = tk.Frame(tbl_frame)
    frameright.pack(side="left", fill="both", expand=True, padx=(3, 0))

    # Bảng tác giả
    columns = ("matg", "tentg")
    bang_tg = ttk.Treeview(frameleft, columns=columns, show="headings", height=12)
    bang_tg.heading("matg", text="Mã tác giả")
    bang_tg.heading("tentg", text="Tên tác giả")
    bang_tg.column("matg", width=180)
    bang_tg.column("tentg", width=520)
    bang_tg.pack(fill="both", expand=True)

  

    def tai_tl():
        # Tải toàn bộ thể loại (TheLoai) từ DB và hiển thị trong bảng thể loại
        for r in bang_theloai.get_children():
            bang_theloai.delete(r)
        try:
            connect = get_connection(); contro = connect.cursor()
            contro.execute("SELECT MaTheLoai, TenTheLoai FROM TheLoai")
            for ma, ten in contro.fetchall():
                clean_ma = ma[0] if isinstance(ma, tuple) else ma
                clean_ten = ten[0] if isinstance(ten, tuple) else ten
                bang_theloai.insert("", "end", values=(clean_ma, clean_ten))
        except Exception as ex:
            # hiển thị cảnh báo lỗi (không cần bọc thêm try/except)
            messagebox.showwarning("Thông báo", f"Không thể tải danh sách Thể loại: {ex}")
        finally:
            if connect:
                try:
                    connect.close()
                except Exception as ex:
                    print("Lỗi khi đóng kết nối (tai_tl):", ex)

    def them_theloai():
        # Mở dialog để thêm một thể loại mới (MaTheLoai, TenTheLoai)
        cuaSo = tk.Toplevel(root)
        cuaSo.title("Thêm thể loại")
        cuaSo.geometry("320x170")

        tk.Label(cuaSo, text="Mã thể loại:").pack(pady=(8, 0))
        ma = tk.Entry(cuaSo, width=36)
        ma.pack(pady=4)

        tk.Label(cuaSo, text="Tên thể loại:").pack(pady=(8, 0))
        ten = tk.Entry(cuaSo, width=36)
        ten.pack(pady=4)

        def save_tl():
            ma = ma.get().strip()
            ten = ten.get().strip()
            if not ma or not ten:
                messagebox.showwarning("Lỗi", "Mã hoặc tên thể loại không được để trống")
                return
            try:
                connect = get_connection(); contro = connect.cursor()
                if check_maloai_trung(connect, ma):
                    messagebox.showerror("Lỗi", "Mã thể loại đã tồn tại")
                    return
                contro.execute("INSERT INTO TheLoai (MaTheLoai, TenTheLoai) VALUES (%s, %s)", (ma, ten))
                connect.commit()
                messagebox.showinfo("Thành công", "Đã thêm thể loại")
                cuaSo.destroy()
                tai_tl()
            except Exception as ex:
                messagebox.showerror("Lỗi", f"Không thể thêm thể loại: {ex}")
            finally:
                if connect:
                    try:
                        connect.close()
                    except Exception as ex:
                        print("Lỗi khi đóng kết nối (thêm thể loại):", ex)

        tk.Button(cuaSo, text="Thêm", width=12, command=save_tl).pack(pady=10)

    # Đặt nút 'Thêm thể loại' cạnh các nút Thêm khác
    tk.Button(khungtop, text="Thêm thể loại", command=them_theloai, width=16).pack(side="right", padx=8)

    # Treeview cho phần thể loại (kích thước nhỏ hơn)
    cot_tl = ("matl", "tentl")
    bang_theloai = ttk.Treeview(frameleft, columns=cot_tl, show="headings", height=5)
    bang_theloai.heading("matl", text="Mã thể loại")
    bang_theloai.heading("tentl", text="Tên thể loại")
    bang_theloai.column("matl", width=120)
    bang_theloai.column("tentl", width=320)
    bang_theloai.pack(fill="both", expand=True, pady=(6,0))

    # ----- Publishers (NXB) UI and table (right) -----
    # Hàm trợ giúp: tải danh sách NXB
    def tai_nxb():
        # Tải toàn bộ nhà xuất bản (NhaXuatBan) từ DB và hiển thị trong bảng NXB
        for r in bang_nxb.get_children():
            bang_nxb.delete(r)
        try:
            connect = get_connection(); contro = connect.cursor()
            contro.execute("SELECT MaNXB, TenNXB FROM NhaXuatBan")
            for ma, ten in contro.fetchall():
                clean_ma = ma[0] if isinstance(ma, tuple) else ma
                clean_ten = ten[0] if isinstance(ten, tuple) else ten
                bang_nxb.insert("", "end", values=(clean_ma, clean_ten))
        except Exception as ex:
            try:
                messagebox.showwarning("Thông báo", f"Không thể tải danh sách NXB: {ex}")
            except Exception:
                pass
        finally:
            try:
                connect.close()
            except Exception:
                pass

    def check_manxb_trung(connect, ma):
        # Kiểm tra xem mã NXB đã tồn tại trong bảng NhaXuatBan hay chưa (dùng trước khi thêm)
        contro = connect.cursor()
        contro.execute("SELECT COUNT(*) FROM NhaXuatBan WHERE MaNXB = %s", (ma,))
        result = contro.fetchone()[0]
        return result > 0

    # Nút 'Thêm NXB' bên cạnh 'Thêm tác giả'
    def them_nxb():
        # Mở dialog để thêm một nhà xuất bản mới (MaNXB, TenNXB)
        cuaSo = tk.Toplevel(root)
        cuaSo.title("Thêm NXB")
        cuaSo.geometry("320x170")

        tk.Label(cuaSo, text="Mã NXB:").pack(pady=(8, 0))
        ma = tk.Entry(cuaSo, width=36)
        ma.pack(pady=4)

        tk.Label(cuaSo, text="Tên NXB:").pack(pady=(8, 0))
        ten = tk.Entry(cuaSo, width=36)
        ten.pack(pady=4)

        def save_nxb():
            ma = ma.get().strip()
            ten = ten.get().strip()
            if not ma or not ten:
                messagebox.showwarning("Lỗi", "Mã hoặc tên NXB không được để trống")
                return
            try:
                connect = get_connection(); contro = connect.cursor()
                if check_manxb_trung(connect, ma):
                    messagebox.showerror("Lỗi", "Mã NXB đã tồn tại")
                    return
                contro.execute("INSERT INTO NhaXuatBan (MaNXB, TenNXB) VALUES (%s, %s)", (ma, ten))
                connect.commit()
                messagebox.showinfo("Thành công", "Đã thêm NXB")
                cuaSo.destroy()
                tai_nxb()
            except Exception as ex:
                messagebox.showerror("Lỗi", f"Không thể thêm NXB: {ex}")
            finally:
                if connect:
                    try:
                        connect.close()
                    except Exception as ex:
                        print("Lỗi khi đóng kết nối (thêm NXB):", ex)

        tk.Button(cuaSo, text="Thêm", width=12, command=save_nxb).pack(pady=10)

    tk.Button(khungtop, text="Thêm NXB", command=them_nxb, width=16).pack(side="right", padx=8)

    # Bảng nhà xuất bản (nhỏ nhất)
    cot_nxb = ("manxb", "tennxb")
    bang_nxb = ttk.Treeview(frameright, columns=cot_nxb, show="headings", height=4)
    bang_nxb.heading("manxb", text="Mã NXB")
    bang_nxb.heading("tennxb", text="Tên NXB")
    bang_nxb.column("manxb", width=100)
    bang_nxb.column("tennxb", width=260)
    bang_nxb.pack(fill="both", expand=True)
    # Nút chỉnh sửa / xóa dùng chung cho tất cả bảng
    def lua_chon():
        # Mở hộp thoại chỉnh sửa/xóa cho bản ghi đang được chọn ở một trong ba bảng (tác giả / thể loại / NXB)
        # Xác định bảng đang được chọn
        chon = None
        bang_nhap = None
        if bang_tg.focus():
            chon = bang_tg.item(bang_tg.focus(), "values")
            bang_nhap = "tacgia"
        elif bang_theloai.focus():
            chon = bang_theloai.item(bang_theloai.focus(), "values")
            bang_nhap = "theloai"
        elif bang_nxb.focus():
            chon = bang_nxb.item(bang_nxb.focus(), "values")
            bang_nhap = "nxb"
        if not chon or not bang_nhap:
            messagebox.showwarning("Chọn dòng", "Vui lòng chon một dòng trong bảng để chỉnh sửa hoặc xóa.")
            return
        # Mở hộp thoại để sửa/xóa
        cuaSo = tk.Toplevel(root)
        cuaSo.title(f"Chỉnh sửa / Xóa - {bang_nhap.capitalize()}")
        cuaSo.geometry("340x200")
        # Các trường (field)
        tk.Label(cuaSo, text=f"Mã {bang_nhap}:").pack()
        ma = tk.Entry(cuaSo, width=36)
        ma.pack(pady=4)
        ma.insert(0, chon[0])
        tk.Label(cuaSo, text=f"Tên {bang_nhap}:").pack()
        ten = tk.Entry(cuaSo, width=36)
        ten.pack(pady=4)
        ten.insert(0, chon[1])
        # Cập nhật
        def chinh_hang():
            ma = ma.get().strip()
            ten = ten.get().strip()
            if not ma or not ten:
                messagebox.showwarning("Lỗi", "Không được để trống")
                return
            try:
                connect = get_connection(); contro = connect.cursor()
                if bang_nhap == "tacgia":
                    contro.execute("UPDATE TacGia SET TenTacGia = %s WHERE MaTacGia = %s", (ten, ma))
                elif bang_nhap == "theloai":
                    contro.execute("UPDATE TheLoai SET TenTheLoai = %s WHERE MaTheLoai = %s", (ten, ma))
                elif bang_nhap == "nxb":
                    contro.execute("UPDATE NhaXuatBan SET TenNXB = %s WHERE MaNXB = %s", (ten, ma))
                connect.commit()
                messagebox.showinfo("Thành công", "Đã cập nhật")
                cuaSo.destroy()
                tai_tg(); tai_tl(); tai_nxb()
            except Exception as ex:
                messagebox.showerror("Lỗi", f"Không thể cập nhật: {ex}")
            finally:
                if connect:
                    try:
                        connect.close()
                    except Exception as ex:
                        print("Lỗi khi đóng kết nối (chinh_hang):", ex)
        # Xóa
        def xoa_hang():
            ma = ma.get().strip()
            if not ma:
                messagebox.showwarning("Lỗi", "Không có mã để xóa")
                return
            if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa '{ma}'?"):
                return
            try:
                connect = get_connection(); contro = connect.cursor()
                if bang_nhap == "tacgia":
                    contro.execute("DELETE FROM TacGia WHERE MaTacGia = %s", (ma,))
                elif bang_nhap == "theloai":
                    contro.execute("DELETE FROM TheLoai WHERE MaTheLoai = %s", (ma,))
                elif bang_nhap == "nxb":
                    contro.execute("DELETE FROM NhaXuatBan WHERE MaNXB = %s", (ma,))
                connect.commit()
                messagebox.showinfo("Thành công", "Đã xóa")
                cuaSo.destroy()
                tai_tg(); tai_tl(); tai_nxb()
            except Exception as ex:
                messagebox.showerror("Lỗi", f"Không thể xóa: {ex}")
            finally:
                if connect:
                    try:
                        connect.close()
                    except Exception as ex:
                        print("Lỗi khi đóng kết nối (xoa_hang):", ex)
        hangnut = tk.Frame(cuaSo)
        hangnut.pack(pady=10)
        tk.Button(hangnut, text="Lưu thay đổi", command=chinh_hang).pack(side="left", padx=8)
        tk.Button(hangnut, text="Xóa", command=xoa_hang).pack(side="left", padx=8)

    btn_shared = tk.Button(khungtop, text="Chỉnh sửa / Xóa mục đã chon", command=lua_chon, width=28)
    btn_shared.pack(side="left", padx=8)

    # Tải dữ liệu ban đầu
    tai_tg()
    tai_nxb()
    tai_tl()

# ===========================================================
# MENU
# ===========================================================
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
menu_bar.add_command(label="Danh Sách", command=show_danh_sach)
menu_bar.add_command(label="Bán Sách", command=show_ban_sach)
menu_bar.add_command(label="Báo Cáo", command=show_bao_cao)
menu_bar.add_command(label="Thông tin Phụ", command=show_thong_tin_phu)

# Hiển thị mặc định

show_ban_sach()
show_danh_sach()

root.mainloop()