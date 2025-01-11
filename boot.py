import rp2
rp2.country('CA')
    

def do_connect():
    import network
    ssid = 'XXXXX'
    wlpassword = 'xxxxx'
    wlan_ip_addr="192.168.0.x"
    wlan_gw_addr="192.168.0.1"
    wlan_dns_addr="8.8.8.8"
    wlan_nmask_addr="255.255.255.0"

    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    if ap_if.active():
        ap_if.active(false)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.ifconfig((wlan_ip_addr,wlan_nmask_addr,wlan_gw_addr,wlan_dns_addr))
        sta_if.connect(ssid,wlpassword)
        while not sta_if.isconnected():
            pass
do_connect()