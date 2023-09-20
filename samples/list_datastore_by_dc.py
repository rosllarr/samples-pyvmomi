from pyVmomi import vim
from tools import cli, service_instance, pchelper

def sizeof_fmt(num):
    """
    Returns the human readable version of a file size

    :param num:
    :return:
    """
    for item in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, item)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

def print_datastore_info(ds_obj):
    summary = ds_obj.summary
    ds_capacity = summary.capacity
    ds_freespace = summary.freeSpace
    ds_uncommitted = summary.uncommitted if summary.uncommitted else 0
    ds_provisioned = ds_capacity - ds_freespace + ds_uncommitted
    ds_overp = ds_provisioned - ds_capacity
    ds_overp_pct = (ds_overp * 100) / ds_capacity \
        if ds_capacity else 0
    print("")
    print("Name                  : {}".format(summary.name))
    print("URL                   : {}".format(summary.url))
    print("Capacity              : {} GB".format(sizeof_fmt(ds_capacity)))
    print("Free Space            : {} GB".format(sizeof_fmt(ds_freespace)))
    print("Uncommitted           : {} GB".format(sizeof_fmt(ds_uncommitted)))
    print("Provisioned           : {} GB".format(sizeof_fmt(ds_provisioned)))
    if ds_overp > 0:
        print("Over-provisioned      : {} GB / {} %".format(
            sizeof_fmt(ds_overp),
            ds_overp_pct))
    print("Hosts                 : {}".format(len(ds_obj.host)))
    print("Virtual Machines      : {}".format(len(ds_obj.vm)))

#def print_datacenter_info(dc_obj):
#    datastore = dc_obj.datastore
#    print(datastore.summary)

def main():
    parser = cli.Parser()
    parser.add_optional_arguments(cli.Argument.DATACENTER_NAME)
    args = parser.get_args()
    si = service_instance.connect(args)

    content = si.RetrieveContent()

    # Get datacenter
    datacenter = pchelper.search_for_obj(content, [vim.Datacenter], args.datacenter_name)
    if datacenter:
        dc_obj = datacenter
    
    ds_obj_list = dc_obj.datastore
    for ds in ds_obj_list:
        print_datastore_info(ds)

if __name__ == "__main__":
    main()
