unit uMain;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, REST.Types, FireDAC.Stan.Intf,
  FireDAC.Stan.Option, FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS,
  FireDAC.Phys.Intf, FireDAC.DApt.Intf, Data.DB, FireDAC.Comp.DataSet,
  FireDAC.Comp.Client, REST.Response.Adapter, REST.Client, Data.Bind.Components,
  Data.Bind.ObjectScope, Vcl.Grids, Vcl.DBGrids, Vcl.StdCtrls;

type
  TfrmMain = class(TForm)
    edtSehir: TEdit;
    cmbSektor: TComboBox;
    btnAra: TButton;
    dbgSonuclar: TDBGrid;
    RestClient: TRESTClient;
    RestRequest: TRESTRequest;
    RestResponse: TRESTResponse;
    RestAdapter: TRESTResponseDataSetAdapter;
    MemTableSonuclar: TFDMemTable;
    dsSonuclar: TDataSource;
    procedure btnAraClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
  private
    { Private declarations }
    procedure APIyeBaglanVeAra(ASehir, ASektor: string);
  public
    { Public declarations }
  end;

var
  frmMain: TfrmMain;

implementation

{$R *.dfm}

procedure TfrmMain.FormCreate(Sender: TObject);
begin
  // Uygulama açıldığında varsayılan ayarlar
  edtSehir.TextHint := 'Şehir Giriniz (Örn: Ankara)';
  cmbSektor.Text := 'Sektör Seçiniz';
end;

procedure TfrmMain.btnAraClick(Sender: TObject);
begin
  // Kullanıcı girişlerini alıp API servisine gönderiyoruz
  APIyeBaglanVeAra(edtSehir.Text, cmbSektor.Text);
end;

procedure TfrmMain.APIyeBaglanVeAra(ASehir, ASektor: string);
begin
  // Eski parametreleri temizle
  RestRequest.Params.Clear;

  // Endpoint: http://localhost:8000/api/v1/companies
  // Eğer kullanıcı değer girdiyse Query Parameter olarak ekle
  if ASehir <> '' then
    RestRequest.AddParameter('sehir', ASehir, pkGETrsUnsaved);

  if (ASektor <> '') and (ASektor <> 'Sektör Seçiniz') then
    RestRequest.AddParameter('sektor', ASektor, pkGETrsUnsaved);

  try
    // İstegi Gönder
    RestRequest.Execute;

    // Gelen HTTP Status Code 200 (OK) ise verileri göster
    if RestResponse.StatusCode = 200 then
    begin
      // RestAdapter otomatik olarak JSON'u MemTable'a çevirecek
      // ve DBGrid üzerinde veriler "Vitrin" olarak listelenecek.
      MemTableSonuclar.Open;
    end
    else
    begin
      ShowMessage('API''den veri alınamadı. Hata Kodu: ' + IntToStr(RestResponse.StatusCode));
    end;
  except
    on E: Exception do
    begin
      // Dev 1 henüz API'yi ayağa kaldırmadıysa bu hata düşer.
      // 1. Gün için bu hatayı almak normaldir.
      ShowMessage('Core API henüz ayakta değil veya ulaşılamıyor: ' + E.Message);
    end;
  end;
end;

end.