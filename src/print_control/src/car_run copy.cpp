#define GW_GRAY_GPIO_CLK 33
#define GW_GRAY_GPIO_DAT 23



int main(int argc, char* argv[])
try {
QCoreApplication a(argc, argv);
using namespace std::chrono_literals;
if (!mycobot::MyCobot::I().IsControllerConnected()) {
    std::cerr << "Robot is not connected\n";
    exit(EXIT_FAILURE);
}
std::cout << "Robot is connected\n";
mycobot::MyCobot::I().PowerOn();
mycobot::MyCobot::I().SleepSecond(1);//需要等待1S，让前面的动作做完

//设置io输出，2、5、26为m5输出引脚
mycobot::MyCobot::I().SetBasicOut(2, 1);
mycobot::MyCobot::I().SleepSecond(1);
mycobot::MyCobot::I().SetBasicOut(5, 1);
mycobot::MyCobot::I().SleepSecond(1);

/*读 取 传 感 器8bit数 据*/
static unsigned char gw_gray_serial_read_simple ()
{
unsigned char ret = 0;
for (int i = 0; i < 8; ++i) {
    mycobot::MyCobot::I().SetDigitalOut(GW_GRAY_GPIO_CLK , 0);//输 出 时 钟 下 降 沿
    ret |= mycobot::MyCobot::I().GetDigitalIn(GW_GRAY_GPIO_DAT) << i; //读 取 数 据 并 存 到ret的 第i位bit
    mycobot::MyCobot::I().SetDigitalOut(GW_GRAY_GPIO_CLK , 1);//输 出 时 钟 上 升 沿
    delayMicroseconds (5);
}
return ret;
}
void setup() { 
pinMode(GW_GRAY_GPIO_CLK , OUTPUT); //设 时 钟 为 输 出
pinMode(GW_GRAY_GPIO_DAT , INPUT_PULLUP); //设 数 据 为 输 入
digitalWrite(GW_GRAY_GPIO_CLK , 0);
//初 始 化 串 口， 方 便 查 看 数 据
Serial.begin (115200);
}
void loop() {
//读 取 传 感 器 串 行 输 出
sensor_status = gw_gray_serial_read_simple ();
//把 读 取 到 的 传 感 器 数 据 打 印 到 公 屏 上
for (int i = 0; i < 8; ++i) {
//获 取 第N位bit
Serial.print(( sensor_status >> i) & 0x1);
Serial.print(" ");
}
Serial.println();
delay (500);
}