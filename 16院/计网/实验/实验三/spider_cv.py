import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from pprint import pprint
import cv2
import numpy as np
import os
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import matplotlib.pyplot as plt
# 设置Matplotlib的字体参数
plt.rcParams['font.family'] = 'SimHei' # 替换为你选择的字体
plt.rcParams['axes.unicode_minus'] = False # 用来正常显示负号

def fetch_weather():
    try:
        # 发送 HTTP 请求
        url = "http://www.nmc.cn/publish/forecast/AGX/guilin.html"
        response = requests.get(url)
        response.encoding = "utf-8"
        html = response.text

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html, "html.parser")
        weather_div = soup.find("div", {"class": "7days day7 pull-right clearfix", "id": "day7"})
        
        # 提取天气数据
        weather_data = []
        if weather_div:
            weather_items = weather_div.find_all("div", {"class": "weather pull-left"})
            for item in weather_items:
                date = item.find("div", {"class": "date"}).text.strip()
                desc_day = item.find_all("div", {"class": "desc"})[0].text.strip()
                desc_night = item.find_all("div", {"class": "desc"})[1].text.strip()
                temp_day = item.find_all("div", {"class": "tmp"})[0].text.strip()
                temp_night = item.find_all("div", {"class": "tmp"})[1].text.strip()
                wind_direction = item.find_all("div", {"class": "windd"})[0].text.strip()
                wind_speed = item.find_all("div", {"class": "winds"})[0].text.strip()

                weather_data.append({
                    "日期": date,
                    "白天天气": desc_day,
                    "夜间天气": desc_night,
                    "白天温度": temp_day,
                    "夜间温度": temp_night,
                    "风向": wind_direction,
                    "风力": wind_speed,
                    "City": "桂林"  
                })

        # 转换为 DataFrame
        weather_df = pd.DataFrame(weather_data)

        # 保存到 Session State
        if not weather_df.empty:
            st.session_state['weather_df'] = weather_df
            st.subheader("天气数据表")
            st.dataframe(weather_df)
        else:
            st.header("获取信息失败...")
    except requests.exceptions.RequestException as e:
        st.error(f"网络请求失败: {e}")
    except Exception as e:
        st.error(f"程序异常: {e}")

def send_email(sender_email, sender_password, recipient_email, subject, body):
    """
    使用 SMTP 发送邮件，处理特定的非致命错误。
    """
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # 连接到 SMTP 服务器并发送邮件
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(sender_email, sender_password)  # 登录
            server.send_message(msg)  # 发送邮件

        return True, None  # 邮件发送成功
    except smtplib.SMTPException as smtp_error:
        # 检查特定的非致命错误
        if str(smtp_error) == "(-1, b'\\x00\\x00\\x00')":
            return True, "邮件已发送，但服务器返回了非致命错误。"
        return False, f"SMTP 错误: {smtp_error}"
    except Exception as e:
        return False, f"未知错误: {e}"

def email_form():
    """
    Streamlit 前端表单，用于发送邮件。
    """
    st.title("模拟发送邮件")

    # 用户输入表单
    st.write("请填写以下信息以发送邮件：")
    sender_email = st.text_input("发件人邮箱", placeholder="your_email@qq.com")
    sender_password = st.text_input("授权码", type="password", placeholder="输入您的QQ邮箱授权码")
    recipient_email = st.text_input("收件人邮箱", placeholder="recipient@example.com")
    subject = st.text_input("邮件主题", placeholder="输入邮件主题")
    body = st.text_area("邮件正文", placeholder="输入邮件内容")

    # 发送按钮
    if st.button("发送邮件"):
        if sender_email and sender_password and recipient_email and subject and body:
            with st.spinner("正在发送邮件，请稍候..."):
                success, error = send_email(sender_email, sender_password, recipient_email, subject, body)

                if success:
                    st.success("邮件发送成功！")
                    # if error:  # 非致命错误提示
                    #     st.info(error)
                else:
                    st.error(f"邮件发送失败：{error}")
        else:
            st.warning("请完整填写所有字段！")

# 登录函数
def QQLogin(driver, email, password):
    """
    本函数主要负责QQ邮箱登录操作
    参数包括
        email-您的登录邮箱
        password-您邮箱所对应的登陆密码
    """
    print("开始登陆操作")
    iframe1 = driver.find_element(By.CLASS_NAME, "QQMailSdkTool_login_loginBox_qq_iframe")
    driver.switch_to.frame(iframe1)
    iframe2 = driver.find_element(By.NAME, 'ptlogin_iframe')
    driver.switch_to.frame(iframe2)
    time.sleep(3)
    driver.find_element(By.XPATH, '//*[@id="switcher_plogin"]').click()
    email_label = driver.find_element(By.XPATH, '//*[@id="u"]')
    email_label.clear()
    email_label.send_keys(email)
    time.sleep(3)
    password_label = driver.find_element(By.XPATH, '//*[@id="p"]')
    password_label.clear()
    password_label.send_keys(password)
    time.sleep(3)
    driver.find_element(By.XPATH, '//*[@id="login_button"]').click()
    time.sleep(20)
    windows = driver.window_handles
    driver.switch_to.window(windows[-1])
    print("登录成功！正在进行邮件发送请稍后...")

# 准备发送邮件函数
def QQSendPrepare(driver, address, title=""):
    """
    本函数主要负责QQ邮箱发送邮件前的收件人和标题键入操作
    参数包括
        address-收件人邮箱地址
        title-邮件主题
    """
    driver.find_element(By.XPATH, '//*[@id="composebtn_td"]').click()
    iframe3 = driver.find_element(By.ID, 'mainFrame')
    driver.switch_to.frame(iframe3)
    driver.find_element(By.XPATH, '/html/body/form[2]/div[2]/div[3]/div[2]/table[2]/tbody/tr/td[2]/div[1]/div[2]/input').send_keys(address)
    driver.find_element(By.XPATH, '/html/body/form[2]/div[2]/div[3]/table[3]/tbody/tr[2]/td[2]/div/div/div/input').send_keys(title)

# 发送邮件的主要函数
def QQSend(driver, address, text, title=""):
    QQSendPrepare(driver, address, title)
    iframe4 = driver.find_element(By.CLASS_NAME, 'qmEditorIfrmEditArea')
    driver.switch_to.frame(iframe4)
    text_label = driver.find_element(By.XPATH, '/html/body/div[1]')
    text_label.clear()
    text_label.send_keys(text)
    driver.switch_to.parent_frame()
    driver.find_element(By.XPATH, '/html/body/form[2]/div[1]/div/a[1]').click()
    WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/div/div[2]/span[2]/a[1]')))
    driver.find_element(By.XPATH, '/html/body/div/div[1]/div/div[1]/div[1]/a').click()
    iframe5 = driver.find_element(By.NAME, 'mailSendStatus')
    driver.switch_to.frame(iframe5)
    status_text = driver.find_element(By.XPATH, "/html/body/div/table/tbody/tr[2]/td[2]/div").get_attribute("title")
    time.sleep(5)
    if status_text == "已投递到对方邮箱":
        driver.quit()
        return "邮件已成功投递"
    return "邮件发送失败"


        
# ====================OpenCV==================================
# 函数：处理上传的 Excel 文件并绘制饼图
def analyze_excel():
    uploaded_file = st.file_uploader("上传 Excel 文件", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        # 加载 Excel 文件
        try:
            data = pd.read_excel(uploaded_file)
            st.write("### 上传的原始数据：")
            st.dataframe(data)
            
            # 检查是否包含所需列
            if "品牌" in data.columns and "市场占有率" in data.columns:
                # 获取品牌和市场占有率列
                labels = data["品牌"]
                sizes = data["市场占有率"]
                
                # 绘制饼状图
                fig, ax = plt.subplots()
                ax.pie(
                    sizes,
                    labels=labels,
                    autopct='%1.1f%%',  # 显示百分比
                    startangle=90,
                    textprops={'fontsize': 10}
                )
                ax.axis('equal')  # 保证饼图为圆形
                plt.title("市场占有率饼状图", fontsize=16)
                
                # 在 Streamlit 中展示图表
                st.pyplot(fig)
            else:
                st.error("数据中缺少 '品牌' 或 '市场占有率' 列，请检查文件格式。")
        except Exception as e:
            st.error(f"文件读取失败：{e}")


# 图像处理函数
def process_image(image_path):
    """
    图像处理：读取图像并进行基本处理（如灰度转换、边缘检测等）。
    :param image_path: 图像文件路径
    :return: 处理后的图像、边缘检测结果
    """
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        st.error("无法读取图像，请检查文件路径。")
        return None, None

    # 转为灰度图像
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 高斯模糊处理，减少噪声
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    # 使用Canny进行边缘检测
    edges = cv2.Canny(blurred_image, 50, 150)

    return image, edges




def main():
    st.title("致谢:由Streamlit提供的可视化界面")
    st.markdown("👉[点击跳转](https://github.com/streamlit/streamlit)--Streamlit官方页面")
    st.write("""
            本应用用于以下内容:\n
             1.爬取中国天气网的天气预报信息并进行可视化展示\n
             2.模拟邮箱发送\n
             3.上传Excel文件并展示、处理与保存\n
             4.使用Pandas数据处理\n
             5.使用OpenCV进行疾病的图像处理和目标识别
        """)

    # 获取天气数据
    st.sidebar.title("组件区")
    action = st.sidebar.radio("选择功能", ["获取天气信息","SMTP模拟发送邮件","密码登入模拟发送邮件", "上传Excel文件并处理", "OpenCV图像处理和目标识别"])

    if action == "获取天气信息":
        st.title("桂林天气爬取与展示")

        # 获取天气信息按钮
        if st.sidebar.button("获取Guilin近七天的天气信息"):
            fetch_weather()

        # 检查数据是否存在
        if 'weather_df' in st.session_state and not st.session_state['weather_df'].empty:
            if st.button("保存到 CSV 文件"):
                try:
                    # 获取脚本所在目录
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    filename = os.path.join(current_dir, "桂林天气数据.csv")

                    # 保存文件
                    st.session_state['weather_df'].to_csv(filename, index=False, encoding="utf-8-sig")
                    st.success(f"数据已保存到文件: {filename}")
                except Exception as e:
                    st.error(f"保存文件时出现错误：{e}")
        else:
            st.warning("当前未获取到任何数据，请先点击侧边栏获取天气信息！")


    elif action=="SMTP模拟发送邮件":
        email_form()
    
    elif action=="密码登入模拟发送邮件":
        st.title("QQ邮箱自动发送邮件")
        # 输入框，收集用户的QQ邮箱信息
        email = st.text_input("请输入您的QQ邮箱账号:")
        password = st.text_input("请输入您的QQ密码:", type="password")
        addressee = st.text_input("请输入收件人的邮箱:")
        text = st.text_area("请输入邮件内容:")
        title = st.text_input("请输入邮件标题:")
        
        # 创建浏览器驱动配置
        option = webdriver.EdgeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option("detach", True)
        
        if st.button("发送邮件"):
            if email and password and addressee and text and title:
                # 配置浏览器驱动
                driver = webdriver.Edge(options=option)
                driver.get("https://mail.qq.com/")
                driver.maximize_window()
                QQLogin(driver, email, password)
                result = QQSend(driver, addressee, text, title)
                st.success(result)
            else:
                st.error("请输入所有必要的字段！")


    elif action == "上传Excel文件并处理":
        st.title("Excel 文件分析与饼图绘制")

        # 调用函数进行上传与分析
        analyze_excel()
    
    elif action == "OpenCV图像处理和目标识别":
        # 设置页面标题
        st.title("OpenCV 图像处理与目标识别")

        # 上传图像文件
        uploaded_file = st.file_uploader("上传图像文件", type=["jpg", "png", "jpeg"])

        if uploaded_file:
            # 读取图像
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if image is not None:
                # 显示原始图像
                st.image(image, channels="BGR", caption="原始图像", use_column_width=True)

                # 转换为灰度图
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # 边缘检测
                edges = cv2.Canny(gray, 100, 200)
                st.image(edges, caption="边缘检测结果", use_column_width=True)

                # 轮廓检测
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # 在图像中绘制轮廓
                contour_image = image.copy()
                cv2.drawContours(contour_image, contours, -1, (0, 0, 255), 2)  # 红色边框

                # 显示轮廓检测结果
                st.image(contour_image, channels="BGR", caption="红色区域识别结果", use_column_width=True)

                # 计算并显示目标数量
                num_objects = len(contours)
                st.write(f"检测到的目标数量：{num_objects}")
            else:
                st.error("无法读取上传的图像，请确保图像格式正确。")
        else:
            st.info("请上传一个图像文件进行处理。")




if __name__ == "__main__":
    main()
