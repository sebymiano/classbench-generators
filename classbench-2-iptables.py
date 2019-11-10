import re

iptablesBinary = "pcn-iptables"
defaultChain = "FORWARD"

srcIP = r'(?P<SrcIp>(?:(?:\d){1,3}\.){3}(?:\d){1,3})\/(?P<SrcNm>(?:\d){1,3})'
dstIP = r'(?P<DstIp>(?:(?:\d){1,3}\.){3}(?:\d){1,3})\/(?P<DstNm>(?:\d){1,3})'
srcPort = r'(?P<SrcPortStart>\d{1,5})(?:\s+):(?:\s+)(?P<SrcPortEnd>\d{1,5})'
dstPort = r'(?P<DstPortStart>\d{1,5})(?:\s+):(?:\s+)(?P<DstPortEnd>\d{1,5})'
IPproto = r'(?:0x)(?P<Proto>[0-9a-fA-F]{1,2})\/(?:0x)(?P<ProtoMask>[0-9a-fA-F]{1,2})'
tcpFlags = r'(?:0x)(?P<TCPFlags>[0-9]{4})\/(?:0x)(?P<TCPFlagsMask>[0-9]{4})'

finalString = fr'@{srcIP}(?:\s+){dstIP}(?:\s+){srcPort}(?:\s+){dstPort}(?:\s+){IPproto}(?:\s+){tcpFlags}'
finalRegex = re.compile(finalString)


def parse_line(line):
    match = finalRegex.search(line)
    return match


def get_src_ip_string(src_ip, src_netmask):
    if int(src_netmask) == 32:
        return f" -s {src_ip}"
    else:
        return f" -s {src_ip}/{src_netmask}"


def get_dst_ip_string(dst_ip, dst_netmask):
    if int(dst_netmask) == 32:
        return f" -d {dst_ip}"
    else:
        return f" -d {dst_ip}/{dst_netmask}"


def get_src_port_string(start, end, start_string):
    start_port = int(start)
    end_port = int(end)
    port_list = list()
    assert (start_port <= 65535 and end_port <= 65535), "Source ports are not correctly formatted"

    if start_port == 0 and end_port == 65535:
        return port_list
    if start_port == end_port:
        port_list.append(start_string + fr" --sport {start_port}")
        return port_list

    while start_port <= end_port:
        port_list.append(start_string + fr" --sport {start_port}")
        start_port += 1
    return port_list


def get_dst_port_string(start, end, start_string):
    start_port = int(start)
    end_port = int(end)
    port_list = list()
    assert (start_port <= 65535 and end_port <= 65535), "Destination ports are not correctly formatted"

    if start_port == 0 and end_port == 65535:
        return port_list
    if start_port == end_port:
        port_list.append(start_string + fr" --dport {start_port}")
        return port_list

    while start_port <= end_port:
        port_list.append(start_string + fr" --dport {start_port}")
        start_port += 1
    return port_list


def parse_and_write_file(input_file, output_file):
    input_lines = 0
    output_lines = 0
    with open(input_file_path, 'r') as input_file, open(output_file_path, 'w') as output_file:
        line = input_file.readline()
        while line:
            input_lines += 1
            string_list = list()
            pcn_iptables_string = fr'{iptablesBinary} -A {defaultChain}'
            string_list.append(pcn_iptables_string)
            # at each line check for a match with a regex
            match = parse_line(line)
            assert match, "The file is not in the expected format!"

            src_ip = match.group('SrcIp')
            src_netmask = match.group('SrcNm')
            dst_ip = match.group('DstIp')
            dst_netmask = match.group('DstNm')
            src_port_start = match.group('SrcPortStart')
            src_port_end = match.group('SrcPortEnd')
            dst_port_start = match.group('DstPortStart')
            dst_port_end = match.group('DstPortEnd')
            proto = match.group('Proto')
            proto_mask = match.group('ProtoMask')
            tcp_flags = match.group('TCPFlags')
            tcp_flags_mask = match.group('TCPFlagsMask')

            string_list = [s + get_src_ip_string(src_ip, src_netmask) for s in string_list]
            string_list = [s + get_dst_ip_string(dst_ip, dst_netmask) for s in string_list]

            for start_str in string_list:
                src_port_res = get_src_port_string(src_port_start, src_port_end, start_str)
                if len(src_port_res) > 0:
                    string_list = src_port_res

            for start_str in string_list:
                dst_port_res = get_dst_port_string(dst_port_start, dst_port_end, start_str)
                if len(dst_port_res) > 0:
                    string_list = dst_port_res

            for item in string_list:
                output_file.write("%s\n" % item)
                output_lines += 1

            line = input_file.readline()

    return input_lines, output_lines


if __name__ == '__main__':
    input_file_path = 'ruleset_acl1_100.txt'
    output_file_path = 'ruleset_acl1_100_out.txt'

    tot_input_lines, tot_output_lines = parse_and_write_file(input_file_path, output_file_path)
    print(f"Read and parsed a total of {tot_input_lines} from file and wrote {tot_output_lines} lines")