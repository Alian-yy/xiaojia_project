import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# 把路径改成你的真实路径（相对路径一般就能用）
img = mpimg.imread("assets/map.png")

fig, ax = plt.subplots()
ax.imshow(img)  # 默认 origin='upper'，y 向下增大，符合像素坐标习惯
ax.set_title("Click on the map to print (x, y). Close window to exit.")
ax.axis("on")

def onclick(event):
    if event.inaxes != ax:
        return
    x = int(round(event.xdata))
    y = int(round(event.ydata))
    print(f"(x_px, y_px) = ({x}, {y})")
    ax.plot([x], [y], marker="o")  # 画个点方便确认
    fig.canvas.draw()

fig.canvas.mpl_connect("button_press_event", onclick)
plt.show()
